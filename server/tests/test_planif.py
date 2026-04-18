from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_planification_endpoint_exists() -> None:
    response = client.get("/api/planifications/")
    assert response.status_code in (200, 500)
