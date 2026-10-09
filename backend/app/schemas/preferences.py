"""Pydantic schemas for user preferences (language and theme)."""

from typing import Literal

from pydantic import BaseModel, Field


class LanguagePreferenceUpdate(BaseModel):
    """Schema for updating language preference."""

    language: Literal["ta", "en"] = Field(..., description="Supported languages: 'ta' (Tamil) or 'en' (English)")


class ThemePreferenceUpdate(BaseModel):
    """Schema for updating visual theme preference."""

    theme: Literal["light", "dark", "system"] = Field(..., description="Supported theme: 'light', 'dark', or 'system'")


class PreferencesResponse(BaseModel):
    """Schema for preference state response."""

    success: bool
    language: str
    theme: str
    message: str
