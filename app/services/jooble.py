"""Service d'accès à l'API Jooble (agrégateur d'offres d'emploi)."""

import requests

from app.core.config import settings

API_BASE_URL = "https://jooble.org/api"
REQUEST_TIMEOUT = 10
SOURCE_NAME = "jooble_api"

BROWSER_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def _empty_result() -> dict:
    """Retourne une structure de résultat vide."""
    return {
        "source": SOURCE_NAME,
        "total": 0,
        "results": [],
    }


def _normalize_offer(job: dict) -> dict:
    """Convertit une offre Jooble vers le format interne JobPilot AI."""
    return {
        "id": job.get("id"),
        "title": job.get("title"),
        "company": job.get("company"),
        "location": job.get("location"),
        "latitude": None,
        "longitude": None,
        "contract": job.get("type"),
        "rome_code": None,
        "source": SOURCE_NAME,
        "url": job.get("link"),
    }


def search_jooble(keyword: str, location: str | None = None) -> dict:
    """
    Recherche des offres via l'API Jooble.

    Args:
        keyword: Mot-clé de recherche.
        location: Ville ou localisation (optionnelle).

    Returns:
        Structure normalisée :
        {
            "source": "...",
            "total": ...,
            "results": [...]
        }
    """

    api_key = settings.jooble_api_key

    if not api_key:
        print("❌ JOOBLE_API_KEY absente.")
        return _empty_result()

    url = f"{API_BASE_URL}/{api_key}"

    payload = {
        "keywords": keyword,
        "location": location or "",
    }

    try:
        response = requests.post(
            url=url,
            json=payload,
            headers=BROWSER_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )

        # ===== DEBUG =====
        print("\n" + "=" * 70)
        print("JOOBLE DEBUG")
        print("=" * 70)
        print(f"URL        : {url}")
        print(f"Payload    : {payload}")
        print(f"Status     : {response.status_code}")
        print(f"Headers    : {dict(response.headers)}")
        print(f"Response   : {response.text}")
        print("=" * 70 + "\n")

    except requests.RequestException as exc:
        print(f"❌ Erreur réseau Jooble : {exc}")
        return _empty_result()

    if response.status_code != 200:
        print(f"❌ Réponse HTTP {response.status_code}")
        return _empty_result()

    try:
        data = response.json()
    except ValueError:
        print("❌ Réponse JSON invalide.")
        return _empty_result()

    offers = data.get("jobs", [])

    return {
        "source": SOURCE_NAME,
        "total": data.get("totalCount", len(offers)),
        "results": [_normalize_offer(job) for job in offers],
    }