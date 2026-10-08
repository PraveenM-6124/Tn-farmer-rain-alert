"""Weather forecasts and hourly data API routes stub.

TODO (Phase 3):
GET /weather
GET /weather/hourly
"""

from fastapi import APIRouter

router = APIRouter(prefix="/weather", tags=["Weather (Phase 3)"])
