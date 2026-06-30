from typing import List

from fastapi import APIRouter, Query

from models.job import Job

from services.jobs_service import get_all_jobs, get_job_by_id, filter_jobs, search_jobs

router = APIRouter()


# 📄 Tous les jobs + filtres
@router.get("/jobs", response_model=List[Job])
def list_jobs(
    title: str = None,
    location: str = None
):
    if title or location:
        return filter_jobs(title=title, location=location)
    return get_all_jobs()


# 🔎 moteur de recherche
@router.get("/search")
def search(q: str = Query(..., description="Recherche globale")):
    return search_jobs(q)


# 📄 détail job
@router.get("/jobs/{job_id}", response_model=Job)
def job_detail(job_id: int):
    job = get_job_by_id(job_id)
    if job:
        return job
    return {"error": "Job not found"}