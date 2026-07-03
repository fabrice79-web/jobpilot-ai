from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.jobs import router as jobs_router
from app.api.routes.search import router as search_router

from app.core.logging_config import setup_logging
import logging


# =========================
# LOGGING
# =========================
setup_logging()
logger = logging.getLogger(__name__)


# =========================
# APP
# =========================
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
# STARTUP LOG
# =========================
logger.info("JobPilot AI started successfully.")


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
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# =========================
# GLOBAL ERROR HANDLER
# =========================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error on {request.url}: {str(exc)}")

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Une erreur interne est survenue. Veuillez réessayer.",
            "code": "INTERNAL_ERROR"
        }
    )