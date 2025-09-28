from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_get_request_by_id():
    created = client.post(
        "/requests",
        json={
            "projectId": "proj_1",
            "title": "Brief",
            "description": "Desc",
        },
    )
    assert created.status_code in (200, 201)
    rid = created.json()["id"]

    resp = client.get(f"/requests/{rid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == rid
