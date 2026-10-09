"""Crop model for tracking farmer crops, growth stage, and agricultural advice."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Crop(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Farmer crop record linked to agricultural advisory rules."""

    __tablename__ = "crops"

    farmer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farmers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    crop_name: Mapped[str] = mapped_column(String(100), nullable=False)  # Paddy, Banana, etc.
    crop_type: Mapped[str] = mapped_column(String(50), default="grain", nullable=False)
    growth_stage: Mapped[str] = mapped_column(
        String(50), default="vegetative", nullable=False
    )  # sowing, vegetative, flowering, maturity, harvesting
    area_acres: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    sowing_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    farmer = relationship("Farmer", back_populates="crops")

    __table_args__ = (Index("idx_crop_farmer_name", "farmer_id", "crop_name"),)

    def __repr__(self) -> str:
        return f"<Crop {self.crop_name} stage={self.growth_stage} acres={self.area_acres}>"
