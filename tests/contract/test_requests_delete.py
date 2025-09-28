from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_delete_request_by_id():
    created = client.post(
        "/requests",
        json={
            "projectId": "proj_1",
            "title": "Brief",
            "description": "Desc",
        },
    )
    rid = created.json()["id"]

    resp = client.delete(f"/requests/{rid}")
    assert resp.status_code == 204
