from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_approve_board():
    rid = client.post(
        "/requests",
        json={"projectId": "proj_1", "title": "Brief", "description": "Desc"},
    ).json()["id"]
    board = client.post(f"/requests/{rid}/boards", json={"summary": "Initial"}).json()

    resp = client.post(f"/boards/{board['id']}/approve")
    assert resp.status_code == 200
    data = resp.json()
    assert data["requestId"] == rid
    assert data["iterationApproved"] >= 1
