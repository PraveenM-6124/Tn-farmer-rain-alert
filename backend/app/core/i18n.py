"""Internationalization (i18n) service for Tamil and English localization."""

import json
from pathlib import Path
from typing import Any

from fastapi import Request

from backend.app.core.config import settings
from backend.app.core.logging import logger

# Directory where translation JSON files are stored
TRANSLATIONS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "translations"

_translations_cache: dict[str, dict[str, str]] = {}


def load_translations() -> dict[str, dict[str, str]]:
    """Load translation files from disk into memory."""
    for lang in settings.SUPPORTED_LANGUAGES:
        file_path = TRANSLATIONS_DIR / f"{lang}.json"
        if file_path.exists():
            try:
                with open(file_path, encoding="utf-8") as f:
                    _translations_cache[lang] = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logger.error("Failed to load translation file %s: %s", file_path, str(e))
                _translations_cache[lang] = {}
        else:
            logger.warning("Translation file does not exist: %s", file_path)
            _translations_cache[lang] = {}
    return _translations_cache


def get_translations() -> dict[str, dict[str, str]]:
    """Get the cached translations or load if empty."""
    if not _translations_cache:
        load_translations()
    return _translations_cache


def t(key: str, lang: str = "ta", **kwargs: Any) -> str:
    """Translate a key into the specified language with fallback and variable interpolation.

    Fallback chain:
    1. Key in requested language
    2. Key in English (en)
    3. The key itself
    """
    translations = get_translations()
    lang_dict = translations.get(lang, {})
    en_dict = translations.get("en", {})

    template = lang_dict.get(key)
    if template is None:
        template = en_dict.get(key, key)

    if kwargs:
        try:
            return template.format(**kwargs)
        except KeyError as e:
            logger.warning("Missing format key %s in translation key '%s'", str(e), key)
            return template

    return template


def resolve_language(request: Request) -> str:
    """Resolve the preferred language for an incoming HTTP request.

    Priority:
    1. Query param ?lang= (e.g. ?lang=ta)
    2. Cookie 'tn_farmer_lang'
    3. Accept-Language header
    4. Default language ('ta')
    """
    # 1. Query parameter
    query_lang = request.query_params.get("lang")
    if query_lang in settings.SUPPORTED_LANGUAGES:
        return query_lang

    # 2. Cookie
    cookie_lang = request.cookies.get(settings.LANGUAGE_COOKIE_NAME)
    if cookie_lang in settings.SUPPORTED_LANGUAGES:
        return cookie_lang

    # 3. Accept-Language header
    accept_lang = request.headers.get("accept-language", "")
    if "ta" in accept_lang.lower():
        return "ta"
    elif "en" in accept_lang.lower():
        return "en"

    # 4. Default fallback
    return settings.DEFAULT_LANGUAGE
