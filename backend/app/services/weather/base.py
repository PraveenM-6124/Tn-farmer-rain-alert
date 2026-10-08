"""Weather provider interface stub.

TODO (Phase 3):
Will define abstract base class WeatherProvider with method:
fetch_forecast(lat: float, lon: float) -> WeatherForecast
"""

from abc import ABC, abstractmethod
from typing import Any


class WeatherProvider(ABC):
    """Abstract interface for weather data providers."""

    @abstractmethod
    async def fetch_forecast(self, latitude: float, longitude: float) -> Any:
        """Fetch normalized weather forecast for given coordinate."""
