"""Routes API pour la recherche et la consultation d'offres d'emploi."""

from typing import Annotated, Optional

from fastapi import APIRouter, Query, HTTPException

from app.services.france_travail import search_france_travail
from app.services.jobs_service import score_job, get_job_by_id

router = APIRouter()

JOB_NOT_FOUND_MESSAGE = "Job not found"


@router.get("/jobs")
def get_jobs(
    keyword: Annotated[str, Query(description="Mot-clé de recherche")] = "",
    location: Annotated[Optional[str], Query(description="Ville")] = None,
) -> dict:
    """Recherche des offres d'emploi selon un mot-clé et une localisation, triées par score."""

    jobs = search_france_travail(keyword, location or "")

    results = jobs.get("results", [])

    enriched = [
        {**job, "score": score_job(job, keyword)}
        for job in results
    ]

    jobs["results"] = sorted(
        enriched,
        key=lambda x: x.get("score", 0),
        reverse=True,
    )
    jobs["total"] = len(jobs["results"])

    return jobs


@router.get(
    "/jobs/{job_id}",
    responses={404: {"description": JOB_NOT_FOUND_MESSAGE}},
)
def get_job(job_id: str) -> dict:
    """Récupère le détail d'une offre d'emploi par son identifiant."""

    job = get_job_by_id(job_id)

    if not job:
        raise HTTPException(status_code=404, detail=JOB_NOT_FOUND_MESSAGE)

    return job