from typing import Annotated, Optional
from fastapi import APIRouter, Query
from app.services.france_travail import search_france_travail

router = APIRouter()


@router.get("/search")
def search_jobs(
    keyword: Annotated[str, Query(description="Mot clé")],
    location: Annotated[Optional[str], Query(description="Ville")] = None
) -> list:
    """Recherche des offres d'emploi et retourne la liste brute des résultats."""
    jobs = search_france_travail(keyword, location)
    return jobs.get("results", [])