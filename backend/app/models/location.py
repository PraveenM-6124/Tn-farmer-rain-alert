"""Location hierarchy model (District -> Taluk -> Village) with PostGIS centroid support."""

import uuid
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Location(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Location entity supporting District, Taluk, and Village hierarchy."""

    __tablename__ = "locations"

    name_en: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    name_ta: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # 'district', 'taluk', 'village'

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    lgd_code: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)

    # PostGIS geometry column (Point with WGS84 SRID 4326)
    centroid = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
        nullable=True,
    )

    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    parent: Mapped[Optional["Location"]] = relationship(
        "Location", remote_side="Location.id", back_populates="children"
    )
    children: Mapped[list["Location"]] = relationship("Location", back_populates="parent", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_location_level_parent", "level", "parent_id"),)

    def __repr__(self) -> str:
        return f"<Location {self.name_en} ({self.name_ta}) [{self.level}]>"
