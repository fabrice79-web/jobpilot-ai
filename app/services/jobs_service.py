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


def _rome_match_score(job: Dict[str, Any], target_rome_codes: set[str]) -> int:
    """Bonus si le code ROME de l'offre correspond aux codes cibles fournis."""
    rome_code = job.get("rome_code")
    return ROME_MATCH_BONUS if rome_code in target_rome_codes else 0

# Termes de niveau de poste qui s'excluent mutuellement : si l'utilisateur
# recherche l'un, une offre titrée avec un autre de ce même groupe est hors-cible,
# même si le code ROME correspond (ROMEO classe par métier, pas par niveau).
JOB_LEVEL_TERMS = ["ingénieur", "technicien", "responsable", "chef de", "directeur", "manager"]


import unicodedata


def _strip_accents(text: str) -> str:
    """Retire les accents d'un texte pour permettre des comparaisons insensibles aux accents."""
    return "".join(
        char for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )


def _job_level_mismatch(job: Dict[str, Any], keyword: str) -> bool:
    """
    Détecte si le titre de l'offre contient un terme de niveau de poste
    différent de celui recherché (ex: recherche 'technicien', offre 'ingénieur').
    """
    keyword_lower = _strip_accents(keyword.lower())
    title_lower = _strip_accents(str(job.get("title", "")).lower())

    searched_level = next(
        (term for term in JOB_LEVEL_TERMS if _strip_accents(term) in keyword_lower),
        None
    )

    if not searched_level:
        return False

    for term in JOB_LEVEL_TERMS:
        term_normalized = _strip_accents(term)
        if term_normalized != _strip_accents(searched_level) and term_normalized in title_lower:
            return True

    return False

JOB_LEVEL_MISMATCH_PENALTY = -50


def score_job(job: Dict[str, Any], keyword: str, target_rome_codes: set[str] | None = None) -> int:
    """
    Calcule le score de pertinence global d'une offre :
    correspondance au mot-clé + ajustement selon le type de contrat
    + bonus si le métier (code ROME) correspond au profil ciblé, uniquement
    si le titre a déjà une pertinence mots-clés minimale (évite les faux
    positifs liés à des offres mal classées par le recruteur)
    + pénalité si le niveau de poste (technicien/ingénieur/...) ne correspond pas.
    """
    keyword = str(keyword).lower()
    codes = target_rome_codes or TARGET_ROME_CODES

    keyword_score = _keyword_relevance_score(job, keyword)
    contract_score = _contract_type_score(job)
    rome_score = _rome_match_score(job, codes) if keyword_score > 0 else 0

    score = keyword_score + contract_score + rome_score

    if _job_level_mismatch(job, keyword):
        score += JOB_LEVEL_MISMATCH_PENALTY

    return score