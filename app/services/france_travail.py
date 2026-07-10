"""Service d'accès à l'API France Travail (offres d'emploi)."""

import time

import requests

from app.core.config import settings

API_ROOT_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2"
API_BASE_URL = f"{API_ROOT_URL}/offres"
SEARCH_ENDPOINT = f"{API_BASE_URL}/search"


TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
TOKEN_SCOPE = "api_offresdemploiv2 o2dsoffre api_romeov2"


GEO_API_URL = "https://geo.api.gouv.fr/communes"
GEO_API_FIELDS = "code,nom,codeDepartement,codesPostaux,population,centre"
DEFAULT_SEARCH_RADIUS_KM = 20

# Paris, Lyon et Marseille sont découpés en arrondissements administratifs.
# L'API France Travail attend le code de chaque arrondissement, pas le code
# "commune agrégée" que renvoie geo.api.gouv.fr par défaut (ex: 75056 pour Paris).
ARRONDISSEMENT_CODES = {
    "75056": [f"751{str(i).zfill(2)}" for i in range(1, 21)],  # Paris
    "69123": [f"6938{i}" for i in range(1, 10)],               # Lyon
    "13055": [f"132{str(i).zfill(2)}" for i in range(1, 17)],  # Marseille
}

REQUEST_TIMEOUT = 10  # secondes — évite le warning Sonar "requests sans timeout"
TOKEN_EXPIRY_MARGIN = 30  # secondes de marge avant expiration réelle du token

# L'API France Travail répond 206 (Partial Content) sur les recherches paginées
# et 204 (No Content) quand aucune offre ne correspond : ce ne sont pas des erreurs.
SUCCESS_STATUS_CODES = (200, 206)

SOURCE_NAME = "france_travail_api"

# Cache mémoire du token (simple, suffisant pour un mono-process)
_token_cache: dict[str, float | str] = {
    "access_token": "",
    "expires_at": 0.0
}


def _empty_result() -> dict:
    """Retourne une structure de résultat vide, utilisée en cas d'échec ou d'absence de données."""
    return {
        "source": SOURCE_NAME,
        "total": 0,
        "results": []
    }


def _normalize_offer(job: dict) -> dict:
    """Normalise une offre brute renvoyée par l'API vers notre format interne."""
    lieu_travail = job.get("lieuTravail", {})

    return {
        "id": job.get("id"),
        "title": job.get("intitule"),
        "company": job.get("entreprise", {}).get("nom"),
        "location": lieu_travail.get("libelle"),
        "latitude": lieu_travail.get("latitude"),
        "longitude": lieu_travail.get("longitude"),
        "contract": job.get("typeContrat"),
        "rome_code": job.get("romeCode")        
    }


def _fetch_new_token() -> str | None:
    """Demande un nouveau token OAuth2 auprès de France Travail."""
    payload = {
        "grant_type": "client_credentials",
        "client_id": settings.france_travail_client_id,
        "client_secret": settings.france_travail_client_secret,
        "scope": TOKEN_SCOPE
    }

    try:
        response = requests.post(TOKEN_URL, data=payload, timeout=REQUEST_TIMEOUT)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    data = response.json()
    access_token = data.get("access_token")
    expires_in = data.get("expires_in", 0)

    if not access_token:
        return None

    _token_cache["access_token"] = access_token
    _token_cache["expires_at"] = time.time() + expires_in - TOKEN_EXPIRY_MARGIN

    return access_token


def _get_access_token() -> str | None:
    """Retourne un token valide, depuis le cache ou en le renouvelant si expiré."""
    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"]:
        return str(_token_cache["access_token"])

    return _fetch_new_token()


def _auth_headers() -> dict[str, str] | None:
    """Construit les headers d'authentification, ou None si le token est indisponible."""
    token = _get_access_token()

    if not token:
        return None

    return {"Authorization": f"Bearer {token}"}


def search_communes(query: str, limit: int = 10) -> list[dict]:
    """
    Recherche toutes les communes correspondant à un nom, pour permettre
    à l'utilisateur de désambiguïser en cas d'homonymie (ex: Allonnes 49 vs 72).

    :param query: nom de ville tapé par l'utilisateur
    :param limit: nombre maximum de suggestions à renvoyer
    :return: liste de {code, nom, codeDepartement, codesPostaux, population, centre}
    """
    if not query:
        return []

    try:
        response = requests.get(
            GEO_API_URL,
            params={
                "nom": query,
                "fields": GEO_API_FIELDS,
                "boost": "population",
                "limit": limit
            },
            timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException:
        return []

    if response.status_code != 200:
        return []

    return response.json()


def _get_commune_code(city_name: str) -> str | None:
    """
    Convertit un nom de ville en code commune INSEE via l'API publique
    geo.api.gouv.fr. En cas d'homonymie, retourne la commune la plus peuplée
    (comportement de repli — préférer commune_code explicite quand disponible).
    """
    communes = search_communes(city_name, limit=1)

    if not communes:
        return None

    return communes[0].get("code")


def get_commune_coordinates(city_name: str) -> tuple[float, float] | None:
    """
    Récupère les coordonnées GPS (latitude, longitude) du centre d'une commune,
    via l'API publique geo.api.gouv.fr.
    """
    communes = search_communes(city_name, limit=1)

    if not communes:
        return None

    centre = communes[0].get("centre", {})
    coordinates = centre.get("coordinates")  # format GeoJSON : [longitude, latitude]

    if not coordinates or len(coordinates) != 2:
        return None

    longitude, latitude = coordinates
    return (latitude, longitude)

MAX_COMMUNES_PER_REQUEST = 5


def _chunk_list(items: list, size: int) -> list[list]:
    """Découpe une liste en sous-listes de taille maximale 'size'."""
    return [items[i:i + size] for i in range(0, len(items), size)]


def _fetch_offers(params: dict[str, str], headers: dict[str, str]) -> list[dict]:
    """Effectue un appel de recherche unique et renvoie la liste d'offres brutes."""
    try:
        response = requests.get(
            SEARCH_ENDPOINT,
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException:
        return []

    if response.status_code == 204:
        return []

    if response.status_code not in SUCCESS_STATUS_CODES:
        return []

    data = response.json()
    return data.get("resultats", [])


def _fetch_offers_for_arrondissements(
    base_params: dict[str, str],
    arrondissements: list[str],
    headers: dict[str, str]
) -> list[dict]:
    """
    Récupère les offres pour une ville multi-arrondissements (Paris/Lyon/Marseille),
    en découpant la recherche en plusieurs appels (max 5 communes/requête) et en
    dédoublonnant les résultats par identifiant d'offre.
    """
    all_offers: list[dict] = []
    seen_ids: set[str] = set()

    for chunk in _chunk_list(arrondissements, MAX_COMMUNES_PER_REQUEST):
        chunk_params = {**base_params, "commune": ",".join(chunk)}
        for offer in _fetch_offers(chunk_params, headers):
            offer_id = offer.get("id")
            if offer_id not in seen_ids:
                seen_ids.add(offer_id)
                all_offers.append(offer)

    return all_offers


def search_france_travail(
    keyword: str,
    location: str | None = None,
    radius_km: int = DEFAULT_SEARCH_RADIUS_KM,
    commune_code: str | None = None
) -> dict:
    """
    Recherche des offres d'emploi via l'API France Travail.

    :param keyword: mot-clé de recherche (obligatoire, peut être vide)
    :param location: nom de ville optionnel (converti en code commune INSEE si commune_code absent)
    :param radius_km: rayon de recherche en km autour de la commune
    :param commune_code: code commune INSEE explicite, prioritaire sur location
    :return: dict normalisé {source, total, results}
    """
    headers = _auth_headers()

    if headers is None:
        return _empty_result()

    resolved_commune_code = commune_code or (_get_commune_code(location) if location else None)
    arrondissements = ARRONDISSEMENT_CODES.get(resolved_commune_code) if resolved_commune_code else None

    base_params: dict[str, str] = {"motsCles": keyword}

    if arrondissements:
        offers = _fetch_offers_for_arrondissements(base_params, arrondissements, headers)
    else:
        if resolved_commune_code:
            base_params["commune"] = resolved_commune_code
            base_params["rayon"] = str(radius_km)
        offers = _fetch_offers(base_params, headers)

    return {
        "source": SOURCE_NAME,
        "total": len(offers),
        "results": [_normalize_offer(job) for job in offers]
    }
