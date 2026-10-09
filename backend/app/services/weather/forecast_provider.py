"""Open-Meteo point forecast integration with async HTTP client."""

from datetime import UTC, datetime

import httpx

from backend.app.core.logging import logger
from backend.app.services.weather.base import (
    HourlyForecastPoint,
    NormalizedForecast,
    WeatherProvider,
)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


class ForecastProvider(WeatherProvider):
    """Fetches real 72-hour hourly forecast from Open-Meteo point forecast API."""

    def __init__(self, timeout_seconds: float = 10.0):
        self.timeout = timeout_seconds

    async def fetch_forecast(self, latitude: float, longitude: float) -> NormalizedForecast:
        params = {
            "latitude": round(latitude, 4),
            "longitude": round(longitude, 4),
            "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,wind_speed_10m,wind_gusts_10m,weather_code",
            "timezone": "UTC",
            "forecast_days": 3,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(OPEN_METEO_URL, params=params)
                response.raise_for_status()
                data = response.json()
            except Exception as exc:
                logger.error("Open-Meteo API call failed for (%f, %f): %s", latitude, longitude, str(exc))
                raise

        hourly_data = data.get("hourly", {})
        times = hourly_data.get("time", [])
        temps = hourly_data.get("temperature_2m", [])
        humids = hourly_data.get("relative_humidity_2m", [])
        probs = hourly_data.get("precipitation_probability", [])
        precips = hourly_data.get("precipitation", [])
        winds = hourly_data.get("wind_speed_10m", [])
        gusts = hourly_data.get("wind_gusts_10m", [])

        now = datetime.now(UTC)
        hourly_points: list[HourlyForecastPoint] = []

        for i in range(min(len(times), 72)):
            ts = datetime.fromisoformat(times[i]).replace(tzinfo=UTC)
            precip = float(precips[i]) if i < len(precips) and precips[i] is not None else 0.0
            prob = float(probs[i]) if i < len(probs) and probs[i] is not None else 0.0
            temp = float(temps[i]) if i < len(temps) and temps[i] is not None else 28.0
            humid = float(humids[i]) if i < len(humids) and humids[i] is not None else 70.0
            wind = float(winds[i]) if i < len(winds) and winds[i] is not None else 10.0
            gust = float(gusts[i]) if i < len(gusts) and gusts[i] is not None else 15.0

            condition = "Rain" if precip > 0.5 else ("Cloudy" if humid > 75 else "Clear")

            hourly_points.append(
                HourlyForecastPoint(
                    timestamp=ts,
                    rain_prob=prob,
                    rainfall_mm=precip,
                    temp_c=temp,
                    humidity=humid,
                    wind_speed_kmh=wind,
                    wind_gusts_kmh=gust,
                    condition=condition,
                )
            )

        return NormalizedForecast(
            latitude=latitude,
            longitude=longitude,
            grid_lat=round(latitude, 1),
            grid_lon=round(longitude, 1),
            source="open-meteo",
            is_mock=False,
            fetched_at=now,
            forecast_issued_at=now,
            imd_warning_level="GREEN",
            hourly=hourly_points,
        )
