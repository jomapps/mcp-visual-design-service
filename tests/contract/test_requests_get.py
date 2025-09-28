from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_list_requests():
    resp = client.get("/requests", params={"projectId": "proj_1", "limit": 1})
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "nextCursor" in data
