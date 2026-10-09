"""Alert generation, deduplication, idempotency enforcement, and quiet hour handling."""

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.logging import logger
from backend.app.models.alert import RainAlert
from backend.app.models.farmer import Farmer
from backend.app.services.crop_advice import get_crop_advice


def is_in_quiet_hours(dt: datetime, quiet_start_hour: int = 21, quiet_end_hour: int = 6) -> bool:
    """Check if time falls in farmer quiet hours (IST)."""
    ist_hour = (dt.hour + 5) % 24  # Approximate IST
    if quiet_start_hour > quiet_end_hour:
        return ist_hour >= quiet_start_hour or ist_hour < quiet_end_hour
    return quiet_start_hour <= ist_hour < quiet_end_hour


def generate_farmer_alert(
    db: Session,
    farmer: Farmer,
    assessment: dict[str, Any],
    alert_type: str = "24h",
) -> RainAlert | None:
    """Generate an alert for a farmer with strict idempotency and bilingual formatting."""
    if not assessment.get("should_alert") and alert_type != "cancellation":
        return None

    event_start = assessment["event_start"]
    event_end = assessment["event_end"]

    # Window key rounded to hour
    start_iso = event_start.strftime("%Y%m%d%H") if event_start else "now"
    idempotency_key = f"{farmer.id}:{start_iso}:{alert_type}"

    # Check for existing alert with same idempotency key
    existing = db.execute(select(RainAlert).where(RainAlert.idempotency_key == idempotency_key)).scalar_one_or_none()
    if existing:
        logger.info("Alert with idempotency key %s already exists. Skipping duplicate.", idempotency_key)
        return existing

    # Check quiet hours (override if SEVERE)
    severity = assessment.get("severity", "MEDIUM")
    now = datetime.now(UTC)
    if is_in_quiet_hours(now) and severity not in ("HIGH", "SEVERE"):
        logger.info("Farmer %s is in quiet hours. Suppressing non-severe alert.", str(farmer.id))
        return None

    # Check daily alert cap (max 3 alerts / day)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    alert_count_today = (
        db.execute(
            select(RainAlert).where(
                RainAlert.farmer_id == farmer.id,
                RainAlert.created_at >= today_start,
            )
        )
        .scalars()
        .all()
    )
    if len(alert_count_today) >= 3 and severity not in ("HIGH", "SEVERE"):
        logger.info("Farmer %s reached daily alert cap (3).", str(farmer.id))
        return None

    # Determine crop action from first registered crop or general advice
    primary_crop = farmer.crops[0].crop_name if farmer.crops else "paddy"
    crop_advice = get_crop_advice(
        crop_name=primary_crop,
        rainfall_24h_mm=assessment.get("cumulative_mm", 20.0),
        wind_gusts_kmh=50.0 if assessment.get("wind_risk") else 15.0,
    )

    location_name = farmer.village or farmer.taluk or farmer.district or "Tamil Nadu"

    # Format English message
    msg_en = (
        f"RAIN ALERT – {location_name.upper()}\n"
        f"Rain is likely {assessment.get('time_window_en', 'in the next 24 hours')}.\n"
        f"Expected rainfall: {assessment.get('rainfall_range', '10–20 mm')}. "
        f"Probability: {int(assessment.get('probability', 75))}%. "
        f"Intensity: {assessment.get('intensity_class', 'Moderate')}.\n"
        f"Recommended action: {crop_advice['advice_en']}"
    )

    # Format Tamil message
    msg_ta = (
        f"மழை எச்சரிக்கை – {location_name}\n"
        f"மழை பெய்ய வாய்ப்பு உள்ளது: {assessment.get('time_window_ta', 'அடுத்த 24 மணி நேரத்தில்')}.\n"
        f"எதிர்பார்க்கப்படும் மழை: {assessment.get('rainfall_range', '10–20 mm')}. "
        f"மழை வாய்ப்பு: {int(assessment.get('probability', 75))}%. "
        f"தீவிரம்: {assessment.get('intensity_class', 'மிதமானது')}.\n"
        f"பரிந்துரைக்கப்படும் நடவடிக்கை: {crop_advice['advice_ta']}"
    )

    alert = RainAlert(
        farmer_id=farmer.id,
        alert_type=alert_type,
        event_start=event_start,
        event_end=event_end,
        rainfall_range=assessment.get("rainfall_range", "20–30 mm"),
        probability=assessment.get("probability", 75.0),
        severity=severity,
        crop_action_en=crop_advice["advice_en"],
        crop_action_ta=crop_advice["advice_ta"],
        message_en=msg_en,
        message_ta=msg_ta,
        idempotency_key=idempotency_key,
        delivery_status="queued",
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    logger.info("Generated new alert %s for farmer %s", str(alert.id), str(farmer.id))
    return alert
