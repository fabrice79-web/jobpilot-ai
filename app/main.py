from fastapi import FastAPI
from app.api.routes.jobs import router as jobs_router
from app.api.routes.search import router as search_router

app = FastAPI(
    title="JobPilot AI",
    description="Moteur de recherche d'emploi (France Travail + APIs futures)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# =========================
# ROUTES
# =========================
app.include_router(jobs_router)
app.include_router(search_router)

# =========================
# ROOT ENDPOINT
# =========================
@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "JobPilot AI API is running 🚀",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# =========================
# HEALTH CHECK (PRO)
# =========================
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
    
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))