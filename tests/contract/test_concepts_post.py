from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_add_concepts_to_board():
    rid = client.post(
        "/requests",
        json={"projectId": "proj_1", "title": "Brief", "description": "Desc"},
    ).json()["id"]
    board = client.post(f"/requests/{rid}/boards", json={"summary": "Initial"}).json()

    payload = {"items": [{"caption": "A", "imageUrls": ["https://example.com/a.jpg"]}]}
    resp = client.post(f"/boards/{board['id']}/concepts", json=payload)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert isinstance(data, list)
    assert data[0]["caption"] == "A"
