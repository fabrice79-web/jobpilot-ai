"""Service d'accès à l'API ROMEO (prédiction IA de codes ROME à partir de texte libre)."""

import requests

from app.services.france_travail import _auth_headers

API_URL = "https://api.francetravail.io/partenaire/romeo/v2/predictionMetiers"
REQUEST_TIMEOUT = 10

CALLER_NAME = "jobpilotai"


def predict_rome_codes(intitule: str, contexte: str | None = None, nb_resultats: int = 3) -> list[dict]:
    """
    Prédit le(s) code(s) ROME correspondant à un texte libre (ex: intitulé de poste recherché).

    :param intitule: texte libre (ex: "technicien méthodes industrialisation")
    :param contexte: secteur d'activité optionnel, améliore la précision de la prédiction
    :param nb_resultats: nombre de prédictions à retourner (1 à 25)
    :return: liste de dicts {codeRome, libelleRome, codeAppellation, libelleAppellation, scorePrediction}
    """
    headers = _auth_headers()

    if headers is None or not intitule:
        return []

    payload = {
        "appellations": [
            {
                "intitule": intitule,
                "identifiant": "1",
                **({"contexte": contexte} if contexte else {})
            }
        ],
        "options": {
            "nomAppelant": CALLER_NAME,
            "nbResultats": nb_resultats
        }
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers={**headers, "Content-Type": "application/json; charset=utf-8"},
            timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException:
        return []

    if response.status_code != 200:
        return []

    data = response.json()

    if not data:
        return []

    return data[0].get("metiersRome", [])