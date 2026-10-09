"""Rain assessment and alert generation models with strict idempotency."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class RainAssessment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Output of pure rain analysis engine evaluating forecast windows."""

    __tablename__ = "rain_assessments"

    grid_lat: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    grid_lon: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    event_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_hours: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    probability: Mapped[float] = mapped_column(Float, nullable=False)  # %
    rainfall_min_mm: Mapped[float] = mapped_column(Float, nullable=False)
    rainfall_max_mm: Mapped[float] = mapped_column(Float, nullable=False)
    intensity_class: Mapped[str] = mapped_column(String(30), nullable=False)  # Light, Moderate, Heavy, etc.

    wind_risk: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    severe_risk: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=85.0, nullable=False)
    should_alert: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class RainAlert(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Farmer-specific rain alert with idempotency key preventing duplicate dispatch."""

    __tablename__ = "rain_alerts"

    farmer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farmers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    alert_type: Mapped[str] = mapped_column(String(20), nullable=False)  # 24h, 12h, 3h, severe, change, cancellation
    event_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    rainfall_range: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "20-30 mm"
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM", nullable=False)  # LOW, MEDIUM, HIGH, SEVERE

    crop_action_en: Mapped[str] = mapped_column(Text, nullable=False)
    crop_action_ta: Mapped[str] = mapped_column(Text, nullable=False)
    message_en: Mapped[str] = mapped_column(Text, nullable=False)
    message_ta: Mapped[str] = mapped_column(Text, nullable=False)

    # Idempotency key: farmer_id:event_window:alert_type
    idempotency_key: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    is_cancelled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    delivery_status: Mapped[str] = mapped_column(String(20), default="queued", nullable=False)

    farmer = relationship("Farmer", back_populates="alerts")
    notifications = relationship("Notification", back_populates="alert", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_alert_farmer_type", "farmer_id", "alert_type"),)
