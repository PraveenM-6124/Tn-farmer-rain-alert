"""Weather forecast and rain analysis API endpoints."""

from fastapi import APIRouter, Query

from backend.app.services.crop_advice import get_crop_advice
from backend.app.services.rain_analysis import analyze_72h_rain_forecast
from backend.app.services.weather.weather_service import weather_service

router = APIRouter(prefix="/weather", tags=["Weather"])

# Default coordinates: Ranipet District, Tamil Nadu
DEFAULT_LAT = 12.9229
DEFAULT_LON = 79.3329


@router.get("/forecast", summary="Get 72-hour hourly forecast")
async def get_forecast(
    latitude: float = Query(default=DEFAULT_LAT, ge=-90.0, le=90.0),
    longitude: float = Query(default=DEFAULT_LON, ge=-180.0, le=180.0),
    force_refresh: bool = Query(default=False),
) -> dict:
    """Return normalized 72-hour weather forecast with grid caching."""
    forecast = await weather_service.get_forecast(latitude, longitude, force_refresh=force_refresh)
    return forecast.model_dump()


@router.get("/assessment", summary="Get analyzed rain assessment and advisory")
async def get_assessment(
    latitude: float = Query(default=DEFAULT_LAT, ge=-90.0, le=90.0),
    longitude: float = Query(default=DEFAULT_LON, ge=-180.0, le=180.0),
    crop_name: str = Query(default="paddy"),
) -> dict:
    """Run pure rain analysis engine and compute crop-specific advisory."""
    forecast = await weather_service.get_forecast(latitude, longitude)
    hourly_dicts = [p.model_dump() for p in forecast.hourly]
    assessment = analyze_72h_rain_forecast(hourly_dicts, imd_warning_level=forecast.imd_warning_level)

    crop_advice = get_crop_advice(
        crop_name=crop_name,
        rainfall_24h_mm=assessment.get("cumulative_mm", 0.0),
        wind_gusts_kmh=50.0 if assessment.get("wind_risk") else 15.0,
    )
    assessment["crop_advice"] = crop_advice
    assessment["provider_source"] = forecast.source
    assessment["is_mock"] = forecast.is_mock
    assessment["imd_warning_level"] = forecast.imd_warning_level
    return assessment
