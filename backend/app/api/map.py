"""Leaflet GIS weather map and rain impact API endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.farmer import Farmer
from backend.app.models.location import Location
from backend.app.services.weather.imd_provider import IMDProvider

router = APIRouter(prefix="/map", tags=["Map"])


@router.get("/rainfall", summary="Get Tamil Nadu district rainfall GeoJSON layer")
def get_rainfall_map(db: Annotated[Session, Depends(get_db)]) -> dict[str, Any]:
    """Return GeoJSON FeatureCollection containing all TN districts with weather attributes."""
    districts = (
        db.execute(select(Location).where(Location.level == "district").order_by(Location.name_en)).scalars().all()
    )

    imd = IMDProvider()
    features = []

    for d in districts:
        warning_color = imd.get_district_warning(d.name_en)
        # Count registered farmers in this district
        farmer_count = db.execute(
            select(func.count(Farmer.id)).where(Farmer.district == d.name_en, Farmer.is_deleted.is_(False))
        ).scalar_one()

        # Synthetic expected rainfall based on warning
        expected_rain = "5–10 mm"
        prob = 40
        if warning_color == "ORANGE":
            expected_rain = "65–95 mm"
            prob = 85
        elif warning_color == "YELLOW":
            expected_rain = "20–35 mm"
            prob = 70

        # Construct GeoJSON Point feature for district centroid
        feature = {
            "type": "Feature",
            "properties": {
                "id": str(d.id),
                "district_en": d.name_en,
                "district_ta": d.name_ta,
                "warning_level": warning_color,
                "expected_rain": expected_rain,
                "rain_prob": prob,
                "affected_farmers": farmer_count,
            },
            "geometry": {
                "type": "Point",
                "coordinates": [d.longitude or 79.0, d.latitude or 11.5],
            },
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features,
    }


@router.get("/impact", summary="Get aggregated rain impact metrics by risk tier")
def get_rain_impact(db: Annotated[Session, Depends(get_db)]) -> dict[str, Any]:
    """Aggregate farmers by risk tier (HIGH, MEDIUM, LOW) across districts."""
    total_farmers = db.execute(select(func.count(Farmer.id)).where(Farmer.is_deleted.is_(False))).scalar_one()
    imd = IMDProvider()

    high_risk_count = 0
    medium_risk_count = 0
    low_risk_count = 0

    farmers = db.execute(select(Farmer).where(Farmer.is_deleted.is_(False))).scalars().all()
    for f in farmers:
        dist = f.district or "Ranipet"
        warn = imd.get_district_warning(dist)
        if warn in ("ORANGE", "RED"):
            high_risk_count += 1
        elif warn == "YELLOW":
            medium_risk_count += 1
        else:
            low_risk_count += 1

    return {
        "total_registered_farmers": total_farmers,
        "high_risk_farmers": high_risk_count,
        "medium_risk_farmers": medium_risk_count,
        "low_risk_farmers": low_risk_count,
        "high_risk_districts": ["Cuddalore", "Nagapattinam", "Nilgiris"],
        "medium_risk_districts": ["Ranipet", "Vellore", "Kancheepuram", "Thanjavur"],
    }
