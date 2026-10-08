"""API package router aggregation."""

from fastapi import APIRouter

from backend.app.api.admin import router as admin_router
from backend.app.api.alerts import router as alerts_router
from backend.app.api.auth import router as auth_router
from backend.app.api.farmers import router as farmers_router
from backend.app.api.health import router as health_router
from backend.app.api.map import router as map_router
from backend.app.api.marketplace import router as marketplace_router
from backend.app.api.preferences import router as preferences_router
from backend.app.api.products import router as products_router
from backend.app.api.weather import router as weather_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(preferences_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(farmers_router)
api_v1_router.include_router(weather_router)
api_v1_router.include_router(alerts_router)
api_v1_router.include_router(products_router)
api_v1_router.include_router(marketplace_router)
api_v1_router.include_router(admin_router)
api_v1_router.include_router(map_router)

__all__ = ["api_v1_router", "health_router"]
