"""Schemas for farmer profile, crops, and location hierarchy."""

import uuid

from pydantic import BaseModel


class CropItem(BaseModel):
    id: uuid.UUID | None = None
    crop_name: str
    crop_type: str = "grain"
    growth_stage: str = "vegetative"
    area_acres: float = 1.0


class CropCreate(BaseModel):
    crop_name: str
    crop_type: str = "grain"
    growth_stage: str = "vegetative"
    area_acres: float = 1.0


class FarmerProfileUpdate(BaseModel):
    name: str | None = None
    language: str | None = "ta"
    theme_preference: str | None = "light"
    district: str | None = None
    taluk: str | None = None
    village: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_consent_given: bool = True


class FarmerProfileResponse(BaseModel):
    id: uuid.UUID
    name: str | None = None
    phone_masked: str
    language: str
    theme_preference: str
    district: str | None = None
    taluk: str | None = None
    village: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_consent_given: bool
    role: str
    crops: list[CropItem] = []


class LocationItem(BaseModel):
    id: uuid.UUID
    name_en: str
    name_ta: str
    level: str
    parent_id: uuid.UUID | None = None
    latitude: float | None = None
    longitude: float | None = None
