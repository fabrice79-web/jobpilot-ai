import json
import os

# Chemin vers le fichier JSON
DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "mock_jobs.json"
)


def load_jobs():
    """Charge les offres d'emploi depuis le fichier JSON."""
    with open(DATA_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def get_all_jobs():
    """Retourne toutes les offres."""
    return load_jobs()


def get_job_by_id(job_id: int):
    """Retourne une offre à partir de son identifiant."""
    jobs = load_jobs()

    for job in jobs:
        if job["id"] == job_id:
            return job

    return None


def filter_jobs(title: str = None, location: str = None):
    """Filtre les offres selon le titre et/ou la localisation."""
    jobs = load_jobs()
    results = []

    for job in jobs:
        if title:
            if title.lower() not in job["title"].lower():
                continue

        if location:
            if location.lower() not in job["location"].lower():
                continue

        results.append(job)

    return results


def search_jobs(query: str):
    """
    Recherche avec un score de pertinence simple.
    Le score est calculé sur le titre, l'entreprise et la localisation.
    """
    jobs = load_jobs()
    query = query.lower()

    results = []

    for job in jobs:
        score = 0

        if query in job["title"].lower():
            score += 3

        if query in job["company"].lower():
            score += 2

        if query in job["location"].lower():
            score += 1

        if score > 0:
            job_result = job.copy()
            job_result["score"] = score
            results.append(job_result)

    results.sort(key=lambda job: job["score"], reverse=True)

    return results