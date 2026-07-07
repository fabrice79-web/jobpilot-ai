import json
import os
from typing import Any, Dict, List, Optional

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "mock_jobs.json"
)

# Bonus/malus appliqués selon le type de contrat (codes officiels France Travail).
# Pas d'exclusion : les offres restent visibles, mais mieux ou moins bien classées.
CONTRACT_TYPE_ADJUSTMENTS: Dict[str, int] = {
    "CDI": 8,    # priorité : CDI
    "MIS": -15,  # intérim : fortement déprécié
    "SAI": -5,   # saisonnier : déprécié
    "LIB": -5,   # profession libérale : hors cible générale
}

# Codes ROME correspondant au profil ciblé par l'utilisateur.
# H1404 : Intervention technique en méthodes et industrialisation
TARGET_ROME_CODES = {"H1404"}
ROME_MATCH_BONUS = 35

def load_jobs() -> List[Dict[str, Any]]:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_all_jobs() -> List[Dict[str, Any]]:
    return load_jobs()


def get_job_by_id(job_id: str) -> Optional[Dict[str, Any]]:
    jobs = load_jobs()
    return next((j for j in jobs if str(j.get("id")) == str(job_id)), None)


def filter_jobs(
    title: Optional[str] = None,
    location: Optional[str] = None
) -> List[Dict[str, Any]]:
    jobs = load_jobs()

    if title:
        jobs = [j for j in jobs if title.lower() in str(j.get("title", "")).lower()]

    if location:
        jobs = [j for j in jobs if location.lower() in str(j.get("location", "")).lower()]

    return jobs


def _keyword_relevance_score(job: Dict[str, Any], keyword: str) -> int:
    """Calcule le score de pertinence basé sur la correspondance de mots-clés."""
    if not keyword:
        return 0

    score = 0

    title = str(job.get("title", "")).lower()
    company = str(job.get("company", "")).lower()
    location = str(job.get("location", "")).lower()

    if keyword in title:
        score += 10

    if keyword in company:
        score += 5

    if keyword in location:
        score += 2

    for word in keyword.split():
        if len(word) < 3:  # ignore les mots trop courts (de, le, un...), trop bruyants
            continue
        if word in title:
            score += 3
        if word in company:
            score += 1

    if title.startswith(keyword):
        score += 5

    return score


def _contract_type_score(job: Dict[str, Any]) -> int:
    """Calcule le bonus/malus lié au type de contrat de l'offre."""
    contract = str(job.get("contract", "")).upper()
    return CONTRACT_TYPE_ADJUSTMENTS.get(contract, 0)


def _rome_match_score(job: Dict[str, Any]) -> int:
    """Bonus si le code ROME de l'offre correspond au profil ciblé."""
    rome_code = job.get("rome_code")
    return ROME_MATCH_BONUS if rome_code in TARGET_ROME_CODES else 0


def score_job(job: Dict[str, Any], keyword: str) -> int:
    """
    Calcule le score de pertinence global d'une offre :
    correspondance au mot-clé + ajustement selon le type de contrat
    + bonus si le métier (code ROME) correspond au profil ciblé.
    """
    keyword = str(keyword).lower()

    return (
        _keyword_relevance_score(job, keyword)
        + _contract_type_score(job)
        + _rome_match_score(job)
    )