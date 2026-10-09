"""Crop-specific agronomic advice engine evaluating weather against TNAU guidelines."""

from pathlib import Path
from typing import Any

import yaml

from backend.app.core.logging import logger

RULES_FILE = Path(__file__).resolve().parent.parent / "data" / "rules" / "crop_rules.yaml"

_cached_rules: list[dict[str, Any]] = []


def load_crop_rules() -> list[dict[str, Any]]:
    """Load crop rules YAML file."""
    global _cached_rules
    if _cached_rules:
        return _cached_rules
    if RULES_FILE.exists():
        try:
            with open(RULES_FILE, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                _cached_rules = data.get("rules", [])
        except Exception as exc:
            logger.error("Failed to load crop rules YAML: %s", str(exc))
            _cached_rules = []
    return _cached_rules


def get_crop_advice(
    crop_name: str,
    rainfall_24h_mm: float,
    wind_gusts_kmh: float = 0.0,
    growth_stage: str = "any",
) -> dict[str, str]:
    """Evaluate applicable advisory for a given crop and weather conditions.

    Returns dictionary containing advice_en and advice_ta.
    """
    rules = load_crop_rules()
    crop_lower = crop_name.lower().strip()
    is_wind_risk = wind_gusts_kmh >= 40.0

    # 1. Look for matching specific rule
    for rule in rules:
        if rule.get("crop") in crop_lower or crop_lower in rule.get("crop", ""):
            # Check rainfall threshold or wind condition
            if rule.get("wind_risk") and is_wind_risk:
                return {
                    "advice_en": rule["advice_en"],
                    "advice_ta": rule["advice_ta"],
                }
            if rainfall_24h_mm >= rule.get("min_rainfall_mm", 0.0):
                return {
                    "advice_en": rule["advice_en"],
                    "advice_ta": rule["advice_ta"],
                }

    # 2. General fallback advisory based on rainfall severity
    if rainfall_24h_mm >= 64.5:
        return {
            "advice_en": "Heavy rain forecast. Ensure adequate drainage trenches across farm plots and protect harvest stacks.",
            "advice_ta": "கனமழை வாய்ப்புள்ளது. வயல்வெளிகளில் வடிகால் வாய்க்கால்களை தூர்வாரி, அறுவடை செய்த பயிர்களை பாதுகாக்கவும்.",
        }
    elif rainfall_24h_mm >= 15.6:
        return {
            "advice_en": "Moderate showers likely. Monitor field moisture and postpone foliar spray applications.",
            "advice_ta": "மிதமான மழை வாய்ப்புள்ளது. நிலத்தின் ஈரப்பதத்தை கவனித்து பூச்சிக்கொல்லி தெளிப்பதை தள்ளிப்போடவும்.",
        }

    return {
        "advice_en": "Normal farm operations may continue. Regularly inspect soil moisture levels.",
        "advice_ta": "வழக்கமான விவசாய பணிகளை தொடரலாம். மண் ஈரப்பதத்தை சீராக கண்காணிக்கவும்.",
    }
