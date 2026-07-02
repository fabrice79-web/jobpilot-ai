import json
import os
from typing import Any, Dict, List, Optional

DATA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "mock_jobs.json"
)


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


def score_job(job: Dict[str, Any], keyword: str) -> int:
    score = 0

    title = str(job.get("title", "")).lower()
    company = str(job.get("company", "")).lower()
    location = str(job.get("location", "")).lower()
    keyword = str(keyword).lower()

    # 🎯 match fort titre
    if keyword in title:
        score += 10

    # 🏢 match entreprise
    if keyword in company:
        score += 5

    # 📍 match localisation
    if keyword in location:
        score += 2

    # 🔎 mots séparés
    words = keyword.split()
    for word in words:
        if word in title:
            score += 3
        if word in company:
            score += 1

    # 🚀 bonus début de titre
    if title.startswith(keyword):
        score += 5

    return score