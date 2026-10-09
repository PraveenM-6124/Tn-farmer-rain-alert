"""FastAPI application entrypoint for Tamil Nadu Farmer Rain Alert & Marketplace."""

import time
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api import api_v1_router, health_router
from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.i18n import load_translations, resolve_language, t
from backend.app.core.logging import logger
from backend.app.core.security import decrypt_phone, mask_phone
from backend.app.models.farmer import Farmer
from backend.app.models.product import Product

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
    allow_origins=["*"] if settings.DEBUG else ["http://tnfarmerweathernoti.com:8000"],
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
async def index_or_language_selection(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """Entrypoint route.

    Requirement:
    On first visit show ONLY language selection.
    If language is already chosen, direct to dashboard.
    """
    cookie_lang = request.cookies.get(settings.LANGUAGE_COOKIE_NAME)
    query_lang = request.query_params.get("lang")

    if query_lang in settings.SUPPORTED_LANGUAGES:
        current_lang = query_lang
        current_theme = request.cookies.get(settings.THEME_COOKIE_NAME, "light")
        response = templates.TemplateResponse(
            request=request,
            name="dashboard.html",
            context={
                "current_lang": current_lang,
                "current_theme": current_theme,
                "selected_district": "Ranipet",
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
            name="dashboard.html",
            context={
                "current_lang": cookie_lang,
                "current_theme": current_theme,
                "selected_district": "Ranipet",
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


@app.get("/dashboard", response_class=HTMLResponse, summary="Farmer Weather & Advisory Dashboard")
async def dashboard_page(
    request: Request,
    district: str | None = "Ranipet",
) -> Response:
    """Main farmer dashboard displaying real-time weather, 72h forecast, and crop advisories."""
    current_lang = resolve_language(request)
    current_theme = request.cookies.get(settings.THEME_COOKIE_NAME, "light")

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "current_lang": current_lang,
            "current_theme": current_theme,
            "selected_district": district or "Ranipet",
        },
    )


@app.get("/map", response_class=HTMLResponse, summary="Tamil Nadu Weather GIS Map")
async def weather_map_page(request: Request) -> Response:
    """Interactive Leaflet GIS map displaying weather severity across all 38 districts."""
    current_lang = resolve_language(request)
    current_theme = request.cookies.get(settings.THEME_COOKIE_NAME, "light")

    return templates.TemplateResponse(
        request=request,
        name="weather_map.html",
        context={
            "current_lang": current_lang,
            "current_theme": current_theme,
        },
    )


@app.get("/marketplace", response_class=HTMLResponse, summary="Agricultural Produce Marketplace")
async def marketplace_page(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """Marketplace browsing page with produce cards and direct contact enquiries."""
    current_lang = resolve_language(request)
    current_theme = request.cookies.get(settings.THEME_COOKIE_NAME, "light")

    products = (
        db.execute(select(Product).where(Product.is_active.is_(True)).order_by(Product.created_at.desc()))
        .scalars()
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="marketplace.html",
        context={
            "current_lang": current_lang,
            "current_theme": current_theme,
            "products": products,
        },
    )


@app.get("/onboarding", response_class=HTMLResponse, summary="Farmer Profile & Onboarding")
async def onboarding_page(request: Request) -> Response:
    """Farmer phone login, OTP verification, and farm profile registration."""
    current_lang = resolve_language(request)
    current_theme = request.cookies.get(settings.THEME_COOKIE_NAME, "light")

    return templates.TemplateResponse(
        request=request,
        name="onboarding.html",
        context={
            "current_lang": current_lang,
            "current_theme": current_theme,
        },
    )


@app.get("/admin-ui", response_class=HTMLResponse, summary="Admin Console UI")
async def admin_dashboard_page(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """Administrative console for telemetry, farmer records, and product moderation."""
    current_lang = resolve_language(request)
    current_theme = request.cookies.get(settings.THEME_COOKIE_NAME, "light")

    farmers_raw = (
        db.execute(select(Farmer).where(Farmer.is_deleted.is_(False)).order_by(Farmer.created_at.desc()))
        .scalars()
        .all()
    )

    farmers = []
    for f in farmers_raw:
        raw_phone = "+919876543210"
        if f.phone_encrypted:
            try:
                raw_phone = decrypt_phone(f.phone_encrypted)
            except Exception:
                pass
        farmers.append(
            {
                "id": str(f.id),
                "name": f.name,
                "phone_masked": mask_phone(raw_phone),
                "district": f.district,
                "taluk": f.taluk,
                "language": f.language,
            }
        )

    products = (
        db.execute(select(Product).where(Product.is_active.is_(True)).order_by(Product.created_at.desc()))
        .scalars()
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "current_lang": current_lang,
            "current_theme": current_theme,
            "farmers": farmers,
            "products": products,
        },
    )
