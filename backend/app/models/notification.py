"""Notification delivery, preferences, and OTP request tracking models."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Notification(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Notification record tracking outbound delivery across SMS, WhatsApp, and Push."""

    __tablename__ = "notifications"

    alert_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("rain_alerts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    farmer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farmers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    channel: Mapped[str] = mapped_column(String(20), nullable=False)  # sms, whatsapp, push
    recipient: Mapped[str] = mapped_column(String(50), nullable=False)  # masked phone or push token
    message: Mapped[str] = mapped_column(Text, nullable=False)
    provider_msg_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="queued", nullable=False
    )  # queued, sent, delivered, failed, dead_letter
    cost_inr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    retry_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    alert = relationship("RainAlert", back_populates="notifications")
    farmer = relationship("Farmer", back_populates="notifications")


class OTPRequest(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Secure OTP tracking model with salt and hashing."""

    __tablename__ = "otp_requests"

    phone_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    otp_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    salt: Mapped[str] = mapped_column(String(32), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (Index("idx_otp_phone_used", "phone_hash", "is_used"),)


class NotificationPreference(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Farmer delivery preference: channels, quiet hours, and daily limits."""

    __tablename__ = "notification_preferences"

    farmer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farmers.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    channels: Mapped[str] = mapped_column(String(50), default="whatsapp,sms", nullable=False)
    quiet_hours_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    quiet_start: Mapped[str] = mapped_column(String(5), default="21:00", nullable=False)  # IST
    quiet_end: Mapped[str] = mapped_column(String(5), default="06:00", nullable=False)  # IST
    max_alerts_per_day: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    farmer = relationship("Farmer", back_populates="notification_preferences")
