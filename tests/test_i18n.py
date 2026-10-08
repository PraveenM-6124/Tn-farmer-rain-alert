"""Tests for internationalization (i18n) and translation parity."""

import json
from pathlib import Path

from backend.app.core.i18n import get_translations, load_translations, t

TRANSLATIONS_DIR = Path(__file__).resolve().parent.parent / "translations"


def test_translation_key_parity() -> None:
    """Ensure translations/en.json and translations/ta.json have identical key sets."""
    en_file = TRANSLATIONS_DIR / "en.json"
    ta_file = TRANSLATIONS_DIR / "ta.json"

    assert en_file.exists(), "translations/en.json must exist"
    assert ta_file.exists(), "translations/ta.json must exist"

    with open(en_file, "r", encoding="utf-8") as f:
        en_keys = set(json.load(f).keys())

    with open(ta_file, "r", encoding="utf-8") as f:
        ta_keys = set(json.load(f).keys())

    missing_in_ta = en_keys - ta_keys
    missing_in_en = ta_keys - en_keys

    assert missing_in_ta == set(), f"Keys missing in ta.json: {missing_in_ta}"
    assert missing_in_en == set(), f"Keys missing in en.json: {missing_in_en}"
    assert en_keys == ta_keys, "Translations must have exact 1:1 key parity"


def test_translate_tamil() -> None:
    """Test lookup of Tamil translation."""
    load_translations()
    val = t("app.title", lang="ta")
    assert "விவசாயி" in val


def test_translate_english() -> None:
    """Test lookup of English translation."""
    load_translations()
    val = t("app.title", lang="en")
    assert val == "Farmer Rain Alert"


def test_translate_fallback_to_english() -> None:
    """Test that missing Tamil keys fall back to English if English key exists."""
    # Simulate a key present only in en
    cache = get_translations()
    cache["en"]["test.dummy_fallback"] = "Fallback English Text"
    try:
        val = t("test.dummy_fallback", lang="ta")
        assert val == "Fallback English Text"
    finally:
        cache["en"].pop("test.dummy_fallback", None)


def test_translate_missing_key_fallback() -> None:
    """Test that nonexistent keys fall back to the key string itself."""
    val = t("completely.nonexistent.key", lang="ta")
    assert val == "completely.nonexistent.key"


def test_translate_variable_interpolation() -> None:
    """Test variable formatting inside translation template."""
    cache = get_translations()
    cache["en"]["test.format_msg"] = "Rain likely in {location} ({mm} mm)"
    try:
        formatted = t("test.format_msg", lang="en", location="Ranipet", mm="25")
        assert formatted == "Rain likely in Ranipet (25 mm)"
    finally:
        cache["en"].pop("test.format_msg", None)
