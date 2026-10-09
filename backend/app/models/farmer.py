"""Farmer model storing preferences (language, theme), location, and consent."""

import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Farmer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Farmer entity containing language/theme preferences, profile details, and location."""

    __tablename__ = "farmers"

    # Profile & Onboarding fields
    name: Mapped[str | None] = mapped_column(String(150), nullable=True)

    # Privacy: phone_hash used for lookup without exposing raw PII; encrypted phone for delivery
    phone_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True, index=True)
    phone_encrypted: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # User Preferences
    language: Mapped[str] = mapped_column(String(5), nullable=False, default="ta", index=True)  # 'ta' or 'en'
    theme_preference: Mapped[str] = mapped_column(
        String(10), nullable=False, default="system"
    )  # 'light', 'dark', 'system'

    # Location references (denormalized strings + optional foreign key)
    district: Mapped[str | None] = mapped_column(String(100), nullable=True)
    taluk: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village: Mapped[str | None] = mapped_column(String(100), nullable=True)

    location_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # GPS coordinates (approximate / centroid default)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Compliance & Account Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_consent_given: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="farmer", nullable=False)

    # Soft delete timestamp for DPDP Act data deletion compliance
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    location = relationship("Location", foreign_keys=[location_id])
    crops = relationship("Crop", back_populates="farmer", cascade="all, delete-orphan")
    alerts = relationship("RainAlert", back_populates="farmer", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="farmer", cascade="all, delete-orphan")
    notification_preferences = relationship(
        "NotificationPreference", back_populates="farmer", uselist=False, cascade="all, delete-orphan"
    )
    products = relationship("Product", back_populates="farmer", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_farmer_lang_theme", "language", "theme_preference"),)

    def __repr__(self) -> str:
        return f"<Farmer id={self.id} lang={self.language} theme={self.theme_preference}>"
