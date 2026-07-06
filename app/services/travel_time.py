"""Service de calcul de durée de trajet via OpenRouteService (mode voiture)."""

import requests

from app.core.config import settings

MATRIX_ENDPOINT = "https://api.openrouteservice.org/v2/matrix/driving-car"
REQUEST_TIMEOUT = 10


def get_driving_durations(
    origin: tuple[float, float],
    destinations: list[tuple[float, float]]
) -> list[int | None]:
    """
    Calcule la durée de trajet en voiture (en minutes) entre une origine
    et plusieurs destinations, en un seul appel API (matrice 1-vers-N).

    :param origin: (latitude, longitude) du point de départ
    :param destinations: liste de (latitude, longitude) des offres
    :return: liste de durées en minutes, alignée sur l'ordre de destinations
             (None si le calcul a échoué pour une destination)
    """
    if not destinations:
        return []

    # OpenRouteService attend les coordonnées en [longitude, latitude]
    locations = [[origin[1], origin[0]]] + [[lon, lat] for lat, lon in destinations]

    payload = {
        "locations": locations,
        "sources": [0],
        "destinations": list(range(1, len(locations))),
        "metrics": ["duration"]
    }

    headers = {
        "Authorization": settings.openrouteservice_api_key,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            MATRIX_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
    except requests.RequestException:
        return [None] * len(destinations)

    if response.status_code != 200:
        return [None] * len(destinations)

    data = response.json()
    durations_seconds = data.get("durations", [[]])[0]

    return [
        round(d / 60) if d is not None else None
        for d in durations_seconds
    ]