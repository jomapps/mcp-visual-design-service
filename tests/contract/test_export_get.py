from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_export_request_metadata():
    rid = client.post(
        "/requests",
        json={"projectId": "proj_1", "title": "Brief", "description": "Desc"},
    ).json()["id"]
    client.post(f"/requests/{rid}/boards", json={"summary": "Initial"}).json()

    resp = client.get(f"/requests/{rid}/export")
    assert resp.status_code == 200
    data = resp.json()
    assert "request" in data and "boards" in data and "concepts" in data
