"""Mock weather provider stub.

TODO (Phase 3):
Returns synthetic hourly forecasts clearly tagged MOCK/DEMO.
"""

from backend.app.services.weather.base import WeatherProvider


class MockWeatherProvider(WeatherProvider):
    async def fetch_forecast(self, latitude: float, longitude: float):
        raise NotImplementedError("MockWeatherProvider will be implemented in Phase 3")
