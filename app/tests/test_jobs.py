from fastapi.testclient import TestClient

from app.main import app
from app.services.jobs_service import get_all_jobs

client = TestClient(app)


def test_get_jobs():
    response = client.get("/jobs")

    assert response.status_code == 200

    data = response.json()

    assert "results" in data
    assert isinstance(data["results"], list)


def test_get_job_by_id():
    jobs = get_all_jobs()

    assert len(jobs) > 0

    job_id = jobs[0]["id"]

    response = client.get(f"/jobs/{job_id}")

    assert response.status_code == 200
    assert response.json()["id"] == job_id


def test_get_job_not_found():
    response = client.get("/jobs/999999")

    assert response.status_code == 404