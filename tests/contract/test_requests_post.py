import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_create_request():
    payload = {
        "projectId": "proj_1",
        "title": "Brief",
        "description": "Desc",
        "tags": ["t"],
        "references": [{"url": "https://example.com"}],
    }
    resp = client.post("/requests", json=payload)
    assert resp.status_code in (201, 200)
    data = resp.json()
    for key in ("id", "projectId", "title", "description", "status", "createdAt"):
        assert key in data
