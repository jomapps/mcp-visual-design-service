from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_create_board_for_request():
    created = client.post(
        "/requests",
        json={"projectId": "proj_1", "title": "Brief", "description": "Desc"},
    )
    rid = created.json()["id"]

    resp = client.post(f"/requests/{rid}/boards", json={"summary": "Initial"})
    assert resp.status_code in (200, 201)
    data = resp.json()
    for key in ("id", "requestId", "iteration", "summary"):
        assert key in data
