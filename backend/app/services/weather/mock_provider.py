"""Mock weather provider generating synthetic 72-hour forecasts tagged MOCK/DEMO."""

import math
from datetime import UTC, datetime, timedelta

from backend.app.core.logging import logger
from backend.app.services.weather.base import (
    HourlyForecastPoint,
    NormalizedForecast,
    WeatherProvider,
)


class MockWeatherProvider(WeatherProvider):
    """Synthetic forecast provider explicitly tagged DEMO/MOCK."""

    async def fetch_forecast(self, latitude: float, longitude: float) -> NormalizedForecast:
        logger.info("[MOCK/DEMO] Generating synthetic 72-hour forecast for (%f, %f)", latitude, longitude)

        now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
        grid_lat = round(latitude, 1)
        grid_lon = round(longitude, 1)

        hourly: list[HourlyForecastPoint] = []

        # Generate 72 hours of realistic diurnal forecast data with an afternoon rain peak
        for hour_idx in range(72):
            ts = now + timedelta(hours=hour_idx)
            hour_of_day = (ts.hour + 5) % 24  # Approximate IST hour

            # Diurnal temperature cycle (24C to 34C)
            temp = 28.0 + 6.0 * math.sin((hour_of_day - 9) * math.pi / 12)
            humidity = 70.0 - 20.0 * math.sin((hour_of_day - 9) * math.pi / 12)

            # Synthetic rain episode on day 1 afternoon (14:00 - 18:00 IST)
            if 14 <= hour_of_day <= 18 and hour_idx < 24:
                rain_prob = 85.0
                rainfall_mm = 6.5
                wind_speed = 22.0
                wind_gusts = 48.0
                condition = "Moderate Rain"
            elif 13 <= hour_of_day <= 19 and 24 <= hour_idx < 48:
                rain_prob = 60.0
                rainfall_mm = 2.0
                wind_speed = 15.0
                wind_gusts = 25.0
                condition = "Light Rain"
            else:
                rain_prob = 10.0
                rainfall_mm = 0.0
                wind_speed = 10.0
                wind_gusts = 15.0
                condition = "Partly Cloudy"

            hourly.append(
                HourlyForecastPoint(
                    timestamp=ts,
                    rain_prob=rain_prob,
                    rainfall_mm=rainfall_mm,
                    temp_c=round(temp, 1),
                    humidity=round(humidity, 1),
                    wind_speed_kmh=round(wind_speed, 1),
                    wind_gusts_kmh=round(wind_gusts, 1),
                    condition=condition,
                )
            )

        return NormalizedForecast(
            latitude=latitude,
            longitude=longitude,
            grid_lat=grid_lat,
            grid_lon=grid_lon,
            source="mock_provider (DEMO/MOCK)",
            is_mock=True,
            fetched_at=now,
            forecast_issued_at=now,
            imd_warning_level="YELLOW",
            hourly=hourly,
        )
