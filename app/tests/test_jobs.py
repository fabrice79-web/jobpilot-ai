from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.jobs_service import get_all_jobs

client = TestClient(app)

FAKE_SEARCH_RESULT = {
    "source": "france_travail_api",
    "total": 1,
    "results": [
        {
            "id": "FAKE001",
            "title": "Développeur Python",
            "company": "ACME",
            "location": "Paris",
            "contract": "CDI",
        }
    ],
}


@patch("app.api.routes.jobs.search_france_travail", return_value=FAKE_SEARCH_RESULT)
def test_get_jobs(mock_search):
    response = client.get("/jobs")

    assert response.status_code == 200

    data = response.json()

    assert "results" in data
    assert isinstance(data["results"], list)
    mock_search.assert_called_once()


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