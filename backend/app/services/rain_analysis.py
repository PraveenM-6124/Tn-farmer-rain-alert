"""Pure functions for rain analysis engine evaluating hourly forecasts and IMD categories."""

from datetime import datetime, timedelta, timezone
from typing import Any


# Official India Meteorological Department (IMD) 24h rainfall intensity categories:
# Light: 2.5 - 15.5 mm | Moderate: 15.6 - 64.4 mm | Heavy: 64.5 - 115.5 mm
# Very Heavy: 115.6 - 204.4 mm | Extremely Heavy: >= 204.5 mm
def classify_imd_intensity(rainfall_mm: float) -> str:
    """Classify 24h cumulative rainfall into official IMD category."""
    if rainfall_mm < 2.5:
        return "Very Light"
    elif rainfall_mm <= 15.5:
        return "Light"
    elif rainfall_mm <= 64.4:
        return "Moderate"
    elif rainfall_mm <= 115.5:
        return "Heavy"
    elif rainfall_mm <= 204.4:
        return "Very Heavy"
    else:
        return "Extremely Heavy"


def format_ist_hour(dt: datetime) -> str:
    """Format hour in Indian Standard Time (IST = UTC + 5:30)."""
    ist_time = (
        dt.astimezone(timezone(timedelta(hours=5, minutes=30))) if dt.tzinfo else dt + timedelta(hours=5, minutes=30)
    )
    hour = ist_time.hour
    am_pm = "AM" if hour < 12 else "PM"
    display_hour = hour % 12
    display_hour = 12 if display_hour == 0 else display_hour
    return f"{display_hour} {am_pm}"


def format_ist_window(start: datetime, end: datetime, lang: str = "en") -> str:
    """Format event start and end as a time window (e.g. 'between 2 PM and 6 PM')."""
    start_str = format_ist_hour(start)
    end_str = format_ist_hour(end)
    if lang == "ta":
        return f"{start_str} முதல் {end_str} மணி வரை"
    return f"between {start_str} and {end_str}"


def calculate_rainfall_range(total_mm: float) -> tuple[float, float, str]:
    """Calculate realistic expected range with uncertainty buffer (e.g. 20–30 mm)."""
    if total_mm <= 5.0:
        min_mm = max(0.0, round(total_mm * 0.7, 1))
        max_mm = round(total_mm * 1.3 + 1.0, 1)
    else:
        min_mm = round(total_mm * 0.8)
        max_mm = round(total_mm * 1.2)
    return min_mm, max_mm, f"{int(min_mm)}–{int(max_mm)} mm"


def analyze_72h_rain_forecast(
    hourly_records: list[dict[str, Any]],
    imd_warning_level: str = "GREEN",
) -> dict[str, Any]:
    """Pure analysis function processing hourly forecast array (up to 72 hours).

    Input record schema:
    [
      {"timestamp": datetime, "rain_prob": 75, "rainfall_mm": 4.5, "wind_speed_kmh": 25, "wind_gusts_kmh": 45},
      ...
    ]
    """
    if not hourly_records:
        return {
            "has_significant_rain": False,
            "probability": 0.0,
            "cumulative_mm": 0.0,
            "rainfall_range": "0 mm",
            "rainfall_min_mm": 0.0,
            "rainfall_max_mm": 0.0,
            "intensity_class": "None",
            "event_start": None,
            "event_end": None,
            "duration_hours": 0.0,
            "time_window_en": "No rain expected",
            "time_window_ta": "மழை வாய்ப்பு இல்லை",
            "wind_risk": False,
            "severe_risk": False,
            "confidence": 95.0,
            "should_alert": False,
            "severity": "LOW",
        }

    total_rain_mm = sum(r.get("rainfall_mm", 0.0) for r in hourly_records)
    max_prob = max((r.get("rain_prob", 0.0) for r in hourly_records), default=0.0)
    max_gusts = max((r.get("wind_gusts_kmh", 0.0) for r in hourly_records), default=0.0)

    # Find rainy hours where rain_prob >= 40% and rainfall_mm >= 0.5
    rain_hours = [r for r in hourly_records if r.get("rain_prob", 0.0) >= 40.0 and r.get("rainfall_mm", 0.0) >= 0.2]

    has_significant_rain = (total_rain_mm >= 5.0 and max_prob >= 50.0) or (imd_warning_level in ("ORANGE", "RED"))

    if rain_hours:
        event_start = rain_hours[0]["timestamp"]
        event_end = rain_hours[-1]["timestamp"] + timedelta(hours=1)
        duration_hours = max(1.0, (event_end - event_start).total_seconds() / 3600.0)
    else:
        event_start = hourly_records[0]["timestamp"]
        event_end = hourly_records[-1]["timestamp"]
        duration_hours = 0.0

    min_mm, max_mm, range_str = calculate_rainfall_range(total_rain_mm)
    intensity_class = classify_imd_intensity(total_rain_mm)

    wind_risk = max_gusts >= 45.0
    severe_risk = imd_warning_level in ("ORANGE", "RED") or total_rain_mm >= 115.5 or max_gusts >= 65.0

    # Determine severity label
    if severe_risk or imd_warning_level == "RED":
        severity = "SEVERE"
    elif total_rain_mm >= 64.5 or imd_warning_level == "ORANGE":
        severity = "HIGH"
    elif total_rain_mm >= 15.6 or imd_warning_level == "YELLOW":
        severity = "MEDIUM"
    else:
        severity = "LOW"

    # Confidence calculation: lower if borderline probability or wide duration
    confidence = 88.0
    if 45.0 <= max_prob <= 65.0:
        confidence -= 15.0
    if imd_warning_level in ("ORANGE", "RED") and total_rain_mm < 10.0:
        confidence -= 20.0  # Provider disagreement buffer

    should_alert = has_significant_rain or (severity in ("HIGH", "SEVERE"))

    return {
        "has_significant_rain": has_significant_rain,
        "probability": round(max_prob, 1),
        "cumulative_mm": round(total_rain_mm, 1),
        "rainfall_range": range_str,
        "rainfall_min_mm": min_mm,
        "rainfall_max_mm": max_mm,
        "intensity_class": intensity_class,
        "event_start": event_start,
        "event_end": event_end,
        "duration_hours": round(duration_hours, 1),
        "time_window_en": format_ist_window(event_start, event_end, lang="en"),
        "time_window_ta": format_ist_window(event_start, event_end, lang="ta"),
        "wind_risk": wind_risk,
        "severe_risk": severe_risk,
        "confidence": max(50.0, round(confidence, 1)),
        "should_alert": should_alert,
        "severity": severity,
    }


def compare_forecast_vs_observation(
    forecast_min_mm: float,
    forecast_max_mm: float,
    observed_mm: float,
) -> dict[str, Any]:
    """Backtesting comparator function measuring forecast accuracy against actual rainfall."""
    within_range = forecast_min_mm <= observed_mm <= forecast_max_mm
    error_mm = round(abs(observed_mm - ((forecast_min_mm + forecast_max_mm) / 2.0)), 2)
    return {
        "forecast_range": f"{forecast_min_mm}–{forecast_max_mm} mm",
        "observed_mm": observed_mm,
        "is_accurate": within_range,
        "error_mm": error_mm,
    }
