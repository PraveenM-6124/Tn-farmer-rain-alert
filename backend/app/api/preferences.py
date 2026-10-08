"""Preferences API endpoints for language and theme management."""

from fastapi import APIRouter, Request, Response

from backend.app.core.config import settings
from backend.app.core.i18n import resolve_language, t
from backend.app.schemas.preferences import (
    LanguagePreferenceUpdate,
    PreferencesResponse,
    ThemePreferenceUpdate,
)

router = APIRouter(prefix="/preferences", tags=["Preferences"])


@router.get("", response_model=PreferencesResponse, summary="Get current preferences")
def get_preferences(request: Request) -> PreferencesResponse:
    """Get active language and theme resolved from cookies/headers."""
    lang = resolve_language(request)
    theme = request.cookies.get(settings.THEME_COOKIE_NAME, "system")
    return PreferencesResponse(
        success=True,
        language=lang,
        theme=theme,
        message="Preferences retrieved",
    )


@router.post(
    "/language",
    response_model=PreferencesResponse,
    summary="Update language preference",
)
def update_language(
    payload: LanguagePreferenceUpdate,
    response: Response,
    request: Request,
) -> PreferencesResponse:
    """Set language preference in cookie (and farmer record if logged in)."""
    # Set 1-year persistent cookie for language
    response.set_cookie(
        key=settings.LANGUAGE_COOKIE_NAME,
        value=payload.language,
        max_age=31536000,
        httponly=False,  # Allow JS access for responsive client updates
        samesite="lax",
    )
    current_theme = request.cookies.get(settings.THEME_COOKIE_NAME, "system")
    return PreferencesResponse(
        success=True,
        language=payload.language,
        theme=current_theme,
        message=t("common.saved", payload.language),
    )


@router.post(
    "/theme",
    response_model=PreferencesResponse,
    summary="Update visual theme preference",
)
def update_theme(
    payload: ThemePreferenceUpdate,
    response: Response,
    request: Request,
) -> PreferencesResponse:
    """Set theme preference (light/dark/system) in cookie."""
    response.set_cookie(
        key=settings.THEME_COOKIE_NAME,
        value=payload.theme,
        max_age=31536000,
        httponly=False,
        samesite="lax",
    )
    current_lang = resolve_language(request)
    return PreferencesResponse(
        success=True,
        language=current_lang,
        theme=payload.theme,
        message="Theme updated successfully",
    )
