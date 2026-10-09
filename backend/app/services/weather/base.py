"""Normalized weather forecast schema and abstract provider interface."""

from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel, Field


class HourlyForecastPoint(BaseModel):
    """Normalized point-in-time forecast record."""

    timestamp: datetime
    rain_prob: float = Field(ge=0.0, le=100.0, description="Rain probability percentage")
    rainfall_mm: float = Field(ge=0.0, description="Precipitation rate mm/h")
    temp_c: float = Field(description="Air temperature in Celsius")
    humidity: float = Field(ge=0.0, le=100.0, description="Relative humidity percentage")
    wind_speed_kmh: float = Field(ge=0.0, description="Wind speed in km/h")
    wind_gusts_kmh: float = Field(ge=0.0, description="Wind gusts in km/h")
    condition: str = Field(default="Clear", description="Weather condition label")


class NormalizedForecast(BaseModel):
    """Standardized multi-day forecast envelope returned by all providers."""

    latitude: float
    longitude: float
    grid_lat: float
    grid_lon: float
    source: str
    is_mock: bool = False
    fetched_at: datetime
    forecast_issued_at: datetime
    imd_warning_level: str = "GREEN"  # GREEN, YELLOW, ORANGE, RED
    hourly: list[HourlyForecastPoint]


class WeatherProvider(ABC):
    """Abstract interface for all forecast providers."""

    @abstractmethod
    async def fetch_forecast(self, latitude: float, longitude: float) -> NormalizedForecast:
        """Fetch and return standardized forecast envelope."""
