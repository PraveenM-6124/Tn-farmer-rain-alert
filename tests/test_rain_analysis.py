"""Tests for pure rain analysis engine, IMD rainfall classification, and backtesting."""

from datetime import UTC, datetime, timedelta

from backend.app.services.rain_analysis import (
    analyze_72h_rain_forecast,
    calculate_rainfall_range,
    classify_imd_intensity,
    compare_forecast_vs_observation,
)


def test_classify_imd_intensity() -> None:
    """Verify official IMD 24h rainfall intensity categories."""
    assert classify_imd_intensity(1.2) == "Very Light"
    assert classify_imd_intensity(10.0) == "Light"
    assert classify_imd_intensity(35.0) == "Moderate"
    assert classify_imd_intensity(85.0) == "Heavy"
    assert classify_imd_intensity(150.0) == "Very Heavy"
    assert classify_imd_intensity(220.0) == "Extremely Heavy"


def test_calculate_rainfall_range() -> None:
    """Verify rainfall range formatting with uncertainty buffer."""
    min_mm, max_mm, range_str = calculate_rainfall_range(25.0)
    assert min_mm == 20.0
    assert max_mm == 30.0
    assert range_str == "20–30 mm"


def test_analyze_72h_rain_forecast_no_rain() -> None:
    """Verify empty/dry forecast evaluation."""
    res = analyze_72h_rain_forecast([])
    assert res["has_significant_rain"] is False
    assert res["cumulative_mm"] == 0.0
    assert res["should_alert"] is False
    assert res["severity"] == "LOW"


def test_analyze_72h_rain_forecast_moderate_rain() -> None:
    """Verify moderate rain scenario generates appropriate alert flags."""
    now = datetime.now(UTC)
    hourly = [
        {
            "timestamp": now + timedelta(hours=i),
            "rain_prob": 70.0,
            "rainfall_mm": 5.0,
            "wind_speed_kmh": 15.0,
            "wind_gusts_kmh": 25.0,
        }
        for i in range(5)
    ]
    res = analyze_72h_rain_forecast(hourly, imd_warning_level="YELLOW")
    assert res["cumulative_mm"] == 25.0
    assert res["intensity_class"] == "Moderate"
    assert res["has_significant_rain"] is True
    assert res["should_alert"] is True
    assert res["severity"] in ("MEDIUM", "HIGH")
    assert "mm" in res["rainfall_range"]


def test_compare_forecast_vs_observation() -> None:
    """Verify backtesting error calculation."""
    res_accurate = compare_forecast_vs_observation(forecast_min_mm=20.0, forecast_max_mm=30.0, observed_mm=25.0)
    assert res_accurate["is_accurate"] is True
    assert res_accurate["error_mm"] == 0.0

    res_miss = compare_forecast_vs_observation(forecast_min_mm=20.0, forecast_max_mm=30.0, observed_mm=45.0)
    assert res_miss["is_accurate"] is False
    assert res_miss["error_mm"] == 20.0
