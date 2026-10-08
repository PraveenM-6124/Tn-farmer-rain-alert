"""Tests for UI routes, language selection gate, and preference APIs."""

from fastapi.testclient import TestClient

from backend.app.core.config import settings


def test_first_visit_shows_only_language_selection(client: TestClient) -> None:
    """Requirement: On first visit show ONLY language selection, no homepage."""
    # When no cookie or query param is passed
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    # Must contain the specified bilingual branding
    assert "FARMER RAIN ALERT" in html
    assert "விவசாயி மழை எச்சரிக்கை" in html
    assert "Choose your language / உங்கள் மொழியைத் தேர்வு செய்யவும்" in html
    # Must have both Tamil and English buttons
    assert "தமிழ்" in html
    assert "English" in html
    assert "TNFarmer.selectLanguage" in html


def test_visit_with_lang_query_sets_cookie_and_shows_dashboard(
    client: TestClient,
) -> None:
    """Selecting language loads the dashboard and sets cookie."""
    response = client.get("/?lang=ta")
    assert response.status_code == 200
    assert settings.LANGUAGE_COOKIE_NAME in response.cookies
    assert response.cookies[settings.LANGUAGE_COOKIE_NAME] == "ta"
    html = response.text
    # Should render dashboard
    assert "வணக்கம்" in html


def test_visit_with_lang_cookie_shows_dashboard_directly(client: TestClient) -> None:
    """Returning user with language cookie bypasses the language select gate."""
    client.cookies.set(settings.LANGUAGE_COOKIE_NAME, "en")
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert "Welcome, Farmer" in html
    assert "Know the rain before it comes" in html


def test_language_selection_page_accessible(client: TestClient) -> None:
    """Dedicated /language route displays the language selection screen."""
    response = client.get("/language")
    assert response.status_code == 200
    html = response.text
    assert "Choose your language" in html


def test_api_update_language_preference(client: TestClient) -> None:
    """POST /api/v1/preferences/language sets the cookie and returns confirmation."""
    response = client.post(
        "/api/v1/preferences/language",
        json={"language": "ta"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["language"] == "ta"
    assert settings.LANGUAGE_COOKIE_NAME in response.cookies
    assert response.cookies[settings.LANGUAGE_COOKIE_NAME] == "ta"


def test_api_update_theme_preference(client: TestClient) -> None:
    """POST /api/v1/preferences/theme sets the theme cookie."""
    response = client.post(
        "/api/v1/preferences/theme",
        json={"theme": "dark"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["theme"] == "dark"
    assert settings.THEME_COOKIE_NAME in response.cookies
    assert response.cookies[settings.THEME_COOKIE_NAME] == "dark"


def test_api_get_preferences(client: TestClient) -> None:
    """GET /api/v1/preferences returns resolved language and theme."""
    client.cookies.set(settings.LANGUAGE_COOKIE_NAME, "ta")
    client.cookies.set(settings.THEME_COOKIE_NAME, "dark")
    response = client.get("/api/v1/preferences")
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "ta"
    assert data["theme"] == "dark"
