from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_list_boards_for_request():
    created = client.post(
        "/requests",
        json={"projectId": "proj_1", "title": "Brief", "description": "Desc"},
    )
    rid = created.json()["id"]
    client.post(f"/requests/{rid}/boards", json={"summary": "Initial"})

    resp = client.get(f"/requests/{rid}/boards")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
