from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_search_jobs():
    response = client.get("/search?keyword=python")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)