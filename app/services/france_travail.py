"""Service d'accès à l'API France Travail (offres d'emploi)."""

import os
import time

import requests

API_BASE_URL = "https://api.francetravail.io/partenaire/offresdemploi/v2/offres"
SEARCH_ENDPOINT = f"{API_BASE_URL}/search"

TOKEN_URL = "https://entreprise.francetravail.fr/connexion/oauth2/access_token?realm=/partenaire"
TOKEN_SCOPE = "api_offresdemploiv2 o2dsoffre"

REQUEST_TIMEOUT = 10  # secondes — évite le warning Sonar "requests sans timeout"
TOKEN_EXPIRY_MARGIN = 30  # secondes de marge avant expiration réelle du token

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
    return {
        "id": job.get("id"),
        "title": job.get("intitule"),
        "company": job.get("entreprise", {}).get("nom"),
        "location": job.get("lieuTravail", {}).get("libelle"),
        "contract": job.get("typeContrat")
    }


def _fetch_new_token() -> str | None:
    """Demande un nouveau token OAuth2 auprès de France Travail."""
    client_id = os.getenv("FRANCE_TRAVAIL_CLIENT_ID")
    client_secret = os.getenv("FRANCE_TRAVAIL_CLIENT_SECRET")

    if not client_id or not client_secret:
        return None

    payload = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
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


def search_france_travail(keyword: str, location: str | None = None) -> dict:
    """
    Recherche des offres d'emploi via l'API France Travail.

    :param keyword: mot-clé de recherche (obligatoire, peut être vide)
    :param location: localisation optionnelle
    :return: dict normalisé {source, total, results}
    """
    headers = _auth_headers()

    if headers is None:
        return _empty_result()

    params: dict[str, str] = {"motsCles": keyword}

    if location:
        params["lieux"] = location

    try:
        response = requests.get(
            SEARCH_ENDPOINT,
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException:
        return _empty_result()

    if response.status_code != 200:
        return _empty_result()

    data = response.json()
    offers = data.get("resultats", [])

    return {
        "source": SOURCE_NAME,
        "total": len(offers),
        "results": [_normalize_offer(job) for job in offers]
    }


def get_offer_by_id(offer_id: str) -> dict | None:
    """
    Récupère le détail d'une offre unique via son identifiant.

    :param offer_id: identifiant de l'offre France Travail
    :return: dict normalisé de l'offre, ou None si introuvable/erreur
    """
    headers = _auth_headers()

    if headers is None:
        return None

    url = f"{API_BASE_URL}/{offer_id}"

    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    return _normalize_offer(response.json())