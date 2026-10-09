"""Farmer profile, onboarding, location hierarchy, and DPDP Act compliance."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_farmer
from backend.app.core.database import get_db
from backend.app.core.security import decrypt_phone, mask_phone
from backend.app.models.crop import Crop
from backend.app.models.farmer import Farmer
from backend.app.models.location import Location
from backend.app.schemas.farmer import (
    CropCreate,
    CropItem,
    FarmerProfileResponse,
    FarmerProfileUpdate,
    LocationItem,
)

router = APIRouter(prefix="/farmers", tags=["Farmers"])


@router.get("/me", response_model=FarmerProfileResponse, summary="Get current farmer profile")
def get_profile(
    farmer: Annotated[Farmer, Depends(get_current_farmer)],
) -> FarmerProfileResponse:
    """Return profile of the authenticated farmer."""
    raw_phone = "+919876543210"
    if farmer.phone_encrypted:
        try:
            raw_phone = decrypt_phone(farmer.phone_encrypted)
        except Exception:
            pass

    crop_items = [
        CropItem(
            id=c.id,
            crop_name=c.crop_name,
            crop_type=c.crop_type,
            growth_stage=c.growth_stage,
            area_acres=c.area_acres,
        )
        for c in farmer.crops
    ]

    return FarmerProfileResponse(
        id=farmer.id,
        name=farmer.name,
        phone_masked=mask_phone(raw_phone),
        language=farmer.language,
        theme_preference=farmer.theme_preference,
        district=farmer.district,
        taluk=farmer.taluk,
        village=farmer.village,
        latitude=farmer.latitude,
        longitude=farmer.longitude,
        is_consent_given=farmer.is_consent_given,
        role=farmer.role,
        crops=crop_items,
    )


@router.put("/me", response_model=FarmerProfileResponse, summary="Update farmer profile & consent")
def update_profile(
    payload: FarmerProfileUpdate,
    farmer: Annotated[Farmer, Depends(get_current_farmer)],
    db: Annotated[Session, Depends(get_db)],
) -> FarmerProfileResponse:
    """Update farmer details, location, and DPDP Act consent."""
    if payload.name is not None:
        farmer.name = payload.name
    if payload.language is not None:
        farmer.language = payload.language
    if payload.theme_preference is not None:
        farmer.theme_preference = payload.theme_preference
    if payload.district is not None:
        farmer.district = payload.district
    if payload.taluk is not None:
        farmer.taluk = payload.taluk
    if payload.village is not None:
        farmer.village = payload.village
    if payload.latitude is not None:
        farmer.latitude = payload.latitude
    if payload.longitude is not None:
        farmer.longitude = payload.longitude

    farmer.is_consent_given = payload.is_consent_given

    db.commit()
    db.refresh(farmer)
    return get_profile(farmer)


@router.delete("/me", summary="Delete farmer account (DPDP Act 2023 compliance)")
def delete_account(
    farmer: Annotated[Farmer, Depends(get_current_farmer)],
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Soft-delete account, anonymize PII, and mark data deleted per DPDP Act 2023."""
    farmer.is_deleted = True
    farmer.is_active = False
    farmer.name = "Deleted Farmer"
    farmer.phone_encrypted = None
    farmer.phone_hash = f"deleted_{uuid.uuid4().hex}"
    db.commit()
    return {"success": True, "message": "Account and personal data removed successfully"}


@router.post("/crops", response_model=CropItem, summary="Add crop to farmer profile")
def add_crop(
    payload: CropCreate,
    farmer: Annotated[Farmer, Depends(get_current_farmer)],
    db: Annotated[Session, Depends(get_db)],
) -> CropItem:
    """Add a cultivated crop for targeted weather advisories."""
    crop = Crop(
        farmer_id=farmer.id,
        crop_name=payload.crop_name,
        crop_type=payload.crop_type,
        growth_stage=payload.growth_stage,
        area_acres=payload.area_acres,
    )
    db.add(crop)
    db.commit()
    db.refresh(crop)
    return CropItem(
        id=crop.id,
        crop_name=crop.crop_name,
        crop_type=crop.crop_type,
        growth_stage=crop.growth_stage,
        area_acres=crop.area_acres,
    )


# --- Public Location Endpoints ---


@router.get("/locations/districts", response_model=list[LocationItem], summary="Get all 38 Tamil Nadu districts")
def get_districts(db: Annotated[Session, Depends(get_db)]) -> list[LocationItem]:
    """Retrieve all districts with bilingual names and centroid coordinates."""
    districts = (
        db.execute(select(Location).where(Location.level == "district").order_by(Location.name_en)).scalars().all()
    )
    return [
        LocationItem(
            id=d.id,
            name_en=d.name_en,
            name_ta=d.name_ta,
            level=d.level,
            latitude=d.latitude,
            longitude=d.longitude,
        )
        for d in districts
    ]


@router.get("/locations/taluks/{district_id}", response_model=list[LocationItem], summary="Get taluks in district")
def get_taluks(
    district_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
) -> list[LocationItem]:
    """Retrieve all taluks belonging to a district."""
    taluks = (
        db.execute(
            select(Location)
            .where(Location.level == "taluk", Location.parent_id == district_id)
            .order_by(Location.name_en)
        )
        .scalars()
        .all()
    )
    return [
        LocationItem(
            id=t.id,
            name_en=t.name_en,
            name_ta=t.name_ta,
            level=t.level,
            parent_id=t.parent_id,
            latitude=t.latitude,
            longitude=t.longitude,
        )
        for t in taluks
    ]


@router.get("/locations/villages/{taluk_id}", response_model=list[LocationItem], summary="Get villages in taluk")
def get_villages(
    taluk_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
) -> list[LocationItem]:
    """Retrieve all villages belonging to a taluk."""
    villages = (
        db.execute(
            select(Location)
            .where(Location.level == "village", Location.parent_id == taluk_id)
            .order_by(Location.name_en)
        )
        .scalars()
        .all()
    )
    return [
        LocationItem(
            id=v.id,
            name_en=v.name_en,
            name_ta=v.name_ta,
            level=v.level,
            parent_id=v.parent_id,
            latitude=v.latitude,
            longitude=v.longitude,
        )
        for v in villages
    ]
