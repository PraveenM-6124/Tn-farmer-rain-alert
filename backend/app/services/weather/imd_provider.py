"""IMD weather provider stub.

TODO (Phase 3):
Will integrate official IMD district warnings, nowcasts, and AWS/ARG station observations.
"""

from backend.app.services.weather.base import WeatherProvider


class IMDProvider(WeatherProvider):
    async def fetch_forecast(self, latitude: float, longitude: float):
        raise NotImplementedError("IMDProvider will be implemented in Phase 3")
