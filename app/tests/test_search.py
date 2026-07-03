from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

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


@patch("app.api.routes.search.search_france_travail", return_value=FAKE_SEARCH_RESULT)
def test_search_jobs(mock_search):
    response = client.get("/search?keyword=python")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    mock_search.assert_called_once()