"""Tests for health and readiness probes."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Verify that /health returns status 200 and 'ok'."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Tamil Nadu Farmer" in data["app_name"]
    assert data["environment"] == "test"


def test_readiness_check(client: TestClient) -> None:
    """Verify that /ready returns status 200 and confirms database connectivity."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"
    assert data["environment"] == "test"
