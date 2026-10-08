"""FastAPI application entrypoint for Tamil Nadu Farmer Rain Alert & Marketplace."""

import time
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from backend.app.api import api_v1_router, health_router
from backend.app.core.config import settings
from backend.app.core.i18n import load_translations, resolve_language, t
from backend.app.core.logging import logger

# Base directory paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = BASE_DIR / "frontend" / "static"
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Location-specific rain alerts and marketplace for Tamil Nadu farmers.",
    version="0.1.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security Headers & Request Timing Middleware
@app.middleware("http")
async def security_and_logging_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    start_time = time.time()
    response: Response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    # Secure HTTP response headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Log request summary without PII
    logger.info(
        "%s %s %d - %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


# Mount Static Assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Jinja2 Templates Setup
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
templates.env.globals["t"] = t


@app.on_event("startup")
async def on_startup() -> None:
    """Preload translations and initialize system on startup."""
    load_translations()
    logger.info(
        "Tamil Nadu Farmer Rain Alert system started successfully in '%s' environment.",
        settings.ENV,
    )


# Health and Readiness Endpoints
app.include_router(health_router)

# API v1 Endpoints
app.include_router(api_v1_router)


# Web UI Routes
@app.get("/", response_class=HTMLResponse, summary="First screen / Homepage")
async def index_or_language_selection(request: Request) -> Response:
    """Entrypoint route.

    Requirement (Section 3):
    On first visit show ONLY language selection, no homepage:
    🌾 FARMER RAIN ALERT / விவசாயி மழை எச்சரிக்கை
    "Choose your language / உங்கள் மொழியைத் தேர்வு செய்யவும்"
    Two large buttons: தமிழ் (ta) and English (en).
    """
    cookie_lang = request.cookies.get(settings.LANGUAGE_COOKIE_NAME)
    query_lang = request.query_params.get("lang")

    # If language has been chosen via query or cookie
    if query_lang in settings.SUPPORTED_LANGUAGES:
        current_lang = query_lang
        current_theme = request.cookies.get(settings.THEME_COOKIE_NAME, "light")
        response = templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "current_lang": current_lang,
                "current_theme": current_theme,
            },
        )
        response.set_cookie(
            key=settings.LANGUAGE_COOKIE_NAME,
            value=current_lang,
            max_age=31536000,
            samesite="lax",
        )
        return response

    if cookie_lang in settings.SUPPORTED_LANGUAGES:
        current_theme = request.cookies.get(settings.THEME_COOKIE_NAME, "light")
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "current_lang": cookie_lang,
                "current_theme": current_theme,
            },
        )

    # First visit: Show ONLY the language selection screen
    return templates.TemplateResponse(
        request=request,
        name="language_select.html",
        context={
            "current_lang": settings.DEFAULT_LANGUAGE,
            "current_theme": "light",
        },
    )


@app.get("/language", response_class=HTMLResponse, summary="Language selector page")
async def language_selection_page(request: Request) -> Response:
    """Dedicated screen to allow farmers to choose or switch language."""
    current_lang = resolve_language(request)
    current_theme = request.cookies.get(settings.THEME_COOKIE_NAME, "light")
    return templates.TemplateResponse(
        request=request,
        name="language_select.html",
        context={
            "current_lang": current_lang,
            "current_theme": current_theme,
        },
    )
