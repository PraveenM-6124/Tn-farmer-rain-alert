"""Point-forecast provider stub (Open-Meteo or equivalent).

TODO (Phase 3):
Point forecast integration returning 72-hour hourly forecasts.
"""

from backend.app.services.weather.base import WeatherProvider


class ForecastProvider(WeatherProvider):
    async def fetch_forecast(self, latitude: float, longitude: float):
        raise NotImplementedError("ForecastProvider will be implemented in Phase 3")
