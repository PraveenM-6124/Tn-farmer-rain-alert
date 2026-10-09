"""Marketplace product listing and masked enquiry models."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Product(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Agricultural product listed by a farmer."""

    __tablename__ = "products"

    farmer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farmers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name_en: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    name_ta: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # grains, vegetables, fruits, pulses, spices

    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(20), default="kg", nullable=False)  # kg, quintal, bag, ton
    price_inr: Mapped[float] = mapped_column(Float, nullable=False)  # Price in INR

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    harvest_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Approximate location for buyer privacy (Village/Taluk/District only)
    district: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    taluk: Mapped[str | None] = mapped_column(String(100), nullable=True)
    village: Mapped[str | None] = mapped_column(String(100), nullable=True)

    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_reported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    farmer = relationship("Farmer", back_populates="products")
    enquiries = relationship("ProductEnquiry", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_product_cat_district", "category", "district"),)


class ProductEnquiry(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Masked in-app enquiry to protect farmer phone number from public web scrapers."""

    __tablename__ = "product_enquiries"

    product_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    buyer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    buyer_phone_masked: Mapped[str] = mapped_column(String(30), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    is_moderated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    product = relationship("Product", back_populates="enquiries")
