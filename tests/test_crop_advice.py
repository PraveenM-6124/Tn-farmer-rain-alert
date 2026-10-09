"""Tests for agronomic crop advice engine and TNAU rules matching."""

from backend.app.services.crop_advice import get_crop_advice


def test_crop_advice_paddy_rain() -> None:
    """Verify paddy advisory for moderate to heavy rainfall."""
    adv = get_crop_advice(crop_name="Paddy (CR 1009)", rainfall_24h_mm=30.0)
    assert "advice_en" in adv
    assert "advice_ta" in adv
    assert len(adv["advice_en"]) > 10
    assert len(adv["advice_ta"]) > 10


def test_crop_advice_banana_wind() -> None:
    """Verify banana advisory triggers propping/staking advice during high winds."""
    adv = get_crop_advice(crop_name="Banana (Grand Naine)", rainfall_24h_mm=10.0, wind_gusts_kmh=45.0)
    assert "advice_en" in adv
    assert "advice_ta" in adv
    # Should recommend staking or protection
    assert (
        "stake" in adv["advice_en"].lower()
        or "propping" in adv["advice_en"].lower()
        or "drainage" in adv["advice_en"].lower()
    )


def test_crop_advice_fallback_dry_weather() -> None:
    """Verify normal farm operations advisory during dry weather."""
    adv = get_crop_advice(crop_name="Unknown Herb", rainfall_24h_mm=0.0)
    assert "advice_en" in adv
    assert "advice_ta" in adv
    assert "normal" in adv["advice_en"].lower() or "continue" in adv["advice_en"].lower()
