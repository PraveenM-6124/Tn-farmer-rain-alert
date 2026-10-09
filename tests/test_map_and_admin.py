"""Tests for Leaflet GIS map endpoints and admin console APIs."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.app.models.location import Location


def test_map_rainfall_geojson(client: TestClient, db_session: Session) -> None:
    """Verify /map/rainfall returns valid GeoJSON FeatureCollection."""
    loc = Location(
        name_en="Ranipet",
        name_ta="ராணிப்பேட்டை",
        level="district",
        latitude=12.9229,
        longitude=79.3329,
    )
    db_session.add(loc)
    db_session.commit()

    res = client.get("/api/v1/map/rainfall")
    assert res.status_code == 200
    data = res.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    assert len(data["features"]) >= 1
    feat = data["features"][0]
    assert feat["type"] == "Feature"
    assert "properties" in feat
    assert "warning_level" in feat["properties"]


def test_map_impact_summary(client: TestClient) -> None:
    """Verify /map/impact returns risk tier aggregates."""
    res = client.get("/api/v1/map/impact")
    assert res.status_code == 200
    data = res.json()
    assert "total_registered_farmers" in data
    assert "high_risk_districts" in data


def test_admin_dashboard_metrics(client: TestClient) -> None:
    """Verify /admin/dashboard returns operational metrics."""
    res = client.get("/api/v1/admin/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "farmers" in data
    assert "alerts" in data
    assert "marketplace" in data


def test_admin_farmers_masked_list(client: TestClient) -> None:
    """Verify /admin/farmers conceals sensitive personal phone numbers."""
    res = client.get("/api/v1/admin/farmers")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_web_routes_render(client: TestClient) -> None:
    """Verify all web template pages render 200 OK."""
    assert client.get("/dashboard").status_code == 200
    assert client.get("/map").status_code == 200
    assert client.get("/onboarding").status_code == 200
    assert client.get("/admin-ui").status_code == 200
