from fastapi import APIRouter, Query
from app.services.france_travail import search_france_travail

router = APIRouter()

@router.get("/search")
def search_jobs(
    q: str = Query(..., description="Mot clé"),
    location: str = None
):
    return search_france_travail(q, location)