"""Basic health check tests."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["service"] == "mcp-visual-design-service"
    assert data["version"] == "0.1.0"
    assert "providers" in data


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["service"] == "MCP Visual Design Service"
    assert data["version"] == "0.1.0"
    assert data["status"] == "running"


def test_styles_endpoint(client):
    """Test styles endpoint."""
    response = client.get("/api/v1/visual/styles")
    assert response.status_code == 200
    
    data = response.json()
    assert "styles" in data
    assert "details" in data
    assert "cinematic" in data["styles"]
    assert "concept-art" in data["styles"]