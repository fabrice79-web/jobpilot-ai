"""Routes API pour la recherche et la consultation d'offres d'emploi."""

from typing import Annotated, Optional

from fastapi import APIRouter, Query, HTTPException

from app.services.france_travail import (
    search_france_travail,
    get_types_contrats_debug,
    get_commune_coordinates,
    search_communes,
)
from app.services.jobs_service import score_job, get_job_by_id
from app.services.travel_time import get_driving_durations

router = APIRouter()

JOB_NOT_FOUND_MESSAGE = "Job not found"

MAX_JOBS_FOR_TRAVEL_TIME = 20


def _enrich_with_travel_duration(jobs: list[dict], depart_ville: str) -> None:
    """
    Ajoute un champ 'travel_duration_minutes' aux offres du top N,
    calculé depuis depart_ville via OpenRouteService (mode voiture).
    Modifie les dicts en place, ne fait rien si la ville est introuvable.
    """
    origin = get_commune_coordinates(depart_ville)

    if origin is None:
        return

    top_jobs = jobs[:MAX_JOBS_FOR_TRAVEL_TIME]

    destinations = [
        (job["latitude"], job["longitude"])
        for job in top_jobs
        if job.get("latitude") is not None and job.get("longitude") is not None
    ]

    if not destinations:
        return

    durations = get_driving_durations(origin, destinations)

    duration_index = 0
    for job in top_jobs:
        if job.get("latitude") is not None and job.get("longitude") is not None:
            job["travel_duration_minutes"] = durations[duration_index]
            duration_index += 1


def _filter_by_max_travel_duration(jobs: list[dict], max_minutes: int) -> list[dict]:
    """
    Ne garde que les offres dont la durée de trajet connue est inférieure ou
    égale à max_minutes. Les offres sans durée calculée (hors top N enrichi,
    ou ville introuvable) sont exclues par précaution, faute d'information fiable.
    """
    return [
        job for job in jobs
        if job.get("travel_duration_minutes") is not None
        and job["travel_duration_minutes"] <= max_minutes
    ]


@router.get("/communes/search")
def communes_search(q: str) -> list[dict]:
    """
    Recherche de communes pour désambiguïsation (ex: menu déroulant côté client
    quand plusieurs communes portent le même nom, comme Allonnes 49 et 72).
    """
    return search_communes(q)


@router.get("/jobs")
def get_jobs(
    keyword: Annotated[str, Query(description="Mot-clé de recherche")] = "",
    location: Annotated[Optional[str], Query(description="Ville")] = None,
    commune_code: Annotated[
        Optional[str],
        Query(description="Code commune INSEE exact (prioritaire sur location, évite les homonymes)")
    ] = None,
    rayon_km: Annotated[int, Query(description="Rayon de recherche en km autour de la ville", ge=0, le=100)] = 20,
    depart_ville: Annotated[
        Optional[str],
        Query(description="Ville de départ pour le calcul de durée de trajet en voiture")
    ] = None,
    max_travel_minutes: Annotated[
        Optional[int],
        Query(description="Durée de trajet maximale en voiture (minutes, circulation fluide). Nécessite depart_ville.", ge=1)
    ] = None,
) -> dict:
    """Recherche des offres d'emploi selon un mot-clé et une localisation, triées par score."""

    jobs = search_france_travail(keyword, location or "", rayon_km, commune_code)

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

    if depart_ville:
        _enrich_with_travel_duration(jobs["results"], depart_ville)

        if max_travel_minutes is not None:
            jobs["results"] = _filter_by_max_travel_duration(jobs["results"], max_travel_minutes)

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


@router.get("/debug/types-contrats")
def debug_types_contrats() -> dict | list:
    """Route temporaire pour explorer les filtres/types de contrats disponibles."""
    return get_types_contrats_debug()