from fastapi import FastAPI
from routes.jobs import router as jobs_router

app = FastAPI(title="JobPilot AI")

app.include_router(jobs_router)


@app.get("/")
def home():
    return {"message": "JobPilot AI API is running"}