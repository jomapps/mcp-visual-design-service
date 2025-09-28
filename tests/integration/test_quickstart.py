from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_quickstart_happy_path():
    # Health
    r = client.get("/health")
    assert r.status_code == 200

    # Create request
    req = client.post(
        "/requests",
        json={
            "projectId": "proj_123",
            "title": "Visual direction",
            "description": "Neo-noir mood board",
            "tags": ["noir", "city"],
            "references": [{"url": "https://example.com/ref.jpg"}],
        },
    ).json()

    # Create board
    board = client.post(f"/requests/{req['id']}/boards", json={"summary": "Initial"}).json()

    # Add concepts
    concepts = client.post(
        f"/boards/{board['id']}/concepts",
        json={"items": [{"caption": "Concept A", "imageUrls": ["https://example.com/a.jpg"]}]},
    ).json()
    assert len(concepts) >= 1

    # Approve board
    appr = client.post(f"/boards/{board['id']}/approve").json()
    assert appr["requestId"] == req["id"]

    # Export
    exp = client.get(f"/requests/{req['id']}/export").json()
    assert "request" in exp and "boards" in exp and "concepts" in exp
