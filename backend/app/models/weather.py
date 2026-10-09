"""Weather forecasts, observations, and spatial grid cache models."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class WeatherForecast(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Normalized hourly forecast keyed by coarse ~0.1 degree grid cell."""

    __tablename__ = "weather_forecasts"

    grid_lat: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    grid_lon: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    timestamp_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    rain_prob: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)  # 0-100%
    rainfall_mm: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    temp_c: Mapped[float] = mapped_column(Float, default=28.0, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, default=70.0, nullable=False)
    wind_speed_kmh: Mapped[float] = mapped_column(Float, default=10.0, nullable=False)
    wind_gusts_kmh: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    condition: Mapped[str] = mapped_column(String(50), default="Clear", nullable=False)
    warning_level: Mapped[str] = mapped_column(
        String(20), default="GREEN", nullable=False
    )  # GREEN, YELLOW, ORANGE, RED

    source: Mapped[str] = mapped_column(String(30), default="open-meteo", nullable=False)
    forecast_issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    __table_args__ = (Index("idx_forecast_grid_time", "grid_lat", "grid_lon", "timestamp_utc", unique=True),)


class WeatherObservation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Observed rainfall from stations (AWS/ARG or IMD)."""

    __tablename__ = "weather_observations"

    station_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    station_name: Mapped[str] = mapped_column(String(100), nullable=False)
    timestamp_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    rainfall_mm: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(30), default="imd", nullable=False)
