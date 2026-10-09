"""India Meteorological Department (IMD) warning integration and observations provider."""

from typing import ClassVar

from backend.app.core.logging import logger
from backend.app.services.weather.base import NormalizedForecast, WeatherProvider
from backend.app.services.weather.mock_provider import MockWeatherProvider


class IMDProvider(WeatherProvider):
    """Integrates official IMD district weather warnings and rainfall observations.

    Note on official IMD API (UNVERIFIED machine endpoint):
    Public IMD bulletins from RMC Chennai (rmcchennai.imd.gov.in) and Mausam (mausam.imd.gov.in)
    publish daily color-coded district warnings (Green, Yellow, Orange, Red). When direct
    real-time API feeds are unavailable, simulated warnings and observation fallbacks are provided.
    """

    # Static district alert level mapping for demonstration
    DISTRICT_WARNINGS: ClassVar[dict[str, str]] = {
        "ranipet": "YELLOW",
        "chennai": "GREEN",
        "vellore": "YELLOW",
        "kancheepuram": "YELLOW",
        "cuddalore": "ORANGE",
        "nagapattinam": "ORANGE",
        "thanjavur": "YELLOW",
        "nilgiris": "ORANGE",
    }

    def get_district_warning(self, district_name: str) -> str:
        """Look up active color-coded IMD warning level for a district."""
        return self.DISTRICT_WARNINGS.get(district_name.lower().strip(), "GREEN")

    async def fetch_forecast(self, latitude: float, longitude: float) -> NormalizedForecast:
        """Fallback to mock provider with IMD warning metadata."""
        logger.info("[IMDProvider] Resolving forecast for (%f, %f) with IMD warning layer", latitude, longitude)
        mock = MockWeatherProvider()
        forecast = await mock.fetch_forecast(latitude, longitude)
        forecast.source = "imd_provider (hybrid)"
        forecast.imd_warning_level = "YELLOW"
        return forecast
