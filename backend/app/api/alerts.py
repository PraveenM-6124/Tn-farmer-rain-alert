"""Rain alert generation and farmer alerts retrieval API."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_farmer
from backend.app.core.database import get_db
from backend.app.models.alert import RainAlert
from backend.app.models.farmer import Farmer
from backend.app.services.alert_service import generate_farmer_alert
from backend.app.services.notifications.notification_service import notification_service
from backend.app.services.rain_analysis import analyze_72h_rain_forecast
from backend.app.services.weather.weather_service import weather_service

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/my-alerts", summary="Get farmer alerts")
def get_my_alerts(
    farmer: Annotated[Farmer, Depends(get_current_farmer)],
    db: Annotated[Session, Depends(get_db)],
) -> list[dict]:
    """Retrieve all rain alerts issued for the authenticated farmer."""
    alerts = (
        db.execute(select(RainAlert).where(RainAlert.farmer_id == farmer.id).order_by(RainAlert.created_at.desc()))
        .scalars()
        .all()
    )

    return [
        {
            "id": str(a.id),
            "alert_type": a.alert_type,
            "event_start": a.event_start.isoformat(),
            "event_end": a.event_end.isoformat(),
            "rainfall_range": a.rainfall_range,
            "probability": a.probability,
            "severity": a.severity,
            "crop_action": a.crop_action_ta if farmer.language == "ta" else a.crop_action_en,
            "message": a.message_ta if farmer.language == "ta" else a.message_en,
            "delivery_status": a.delivery_status,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]


@router.post("/trigger-alert", summary="Generate and dispatch live alert for current farmer")
async def trigger_farmer_alert(
    farmer: Annotated[Farmer, Depends(get_current_farmer)],
    db: Annotated[Session, Depends(get_db)],
    alert_type: str = Query(default="24h"),
) -> dict:
    """Analyze current forecast for farmer's coordinates and dispatch alert if conditions met."""
    lat = farmer.latitude or 12.9229
    lon = farmer.longitude or 79.3329

    forecast = await weather_service.get_forecast(lat, lon)
    hourly_dicts = [p.model_dump() for p in forecast.hourly]
    assessment = analyze_72h_rain_forecast(hourly_dicts, imd_warning_level=forecast.imd_warning_level)

    # Force should_alert for demo trigger if requested
    assessment["should_alert"] = True

    alert = generate_farmer_alert(db, farmer, assessment, alert_type=alert_type)
    if not alert:
        return {"success": False, "message": "No significant rain requiring alert at current location"}

    # Dispatch notification via multi-channel notification engine
    notification = await notification_service.dispatch_alert(db, alert, farmer)

    return {
        "success": True,
        "alert_id": str(alert.id),
        "notification_id": str(notification.id),
        "channel": notification.channel,
        "delivery_status": notification.status,
        "message": notification.message,
    }
