"""Initial locations and farmers tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-08 21:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Ensure postgis extension exists when on PostgreSQL
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # 1. locations table
    op.create_table(
        "locations",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name_en", sa.String(length=120), nullable=False),
        sa.Column("name_ta", sa.String(length=120), nullable=False),
        sa.Column("level", sa.String(length=20), nullable=False),
        sa.Column("parent_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("lgd_code", sa.String(length=30), nullable=True),
        sa.Column(
            "centroid",
            Geometry(geometry_type="POINT", srid=4326, spatial_index=True),
            nullable=True,
        ),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["parent_id"], ["locations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_locations_name_en"), "locations", ["name_en"], unique=False)
    op.create_index(op.f("ix_locations_name_ta"), "locations", ["name_ta"], unique=False)
    op.create_index(op.f("ix_locations_level"), "locations", ["level"], unique=False)
    op.create_index(op.f("ix_locations_lgd_code"), "locations", ["lgd_code"], unique=False)
    op.create_index("idx_location_level_parent", "locations", ["level", "parent_id"], unique=False)

    # 2. farmers table
    op.create_table(
        "farmers",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=True),
        sa.Column("phone_hash", sa.String(length=64), nullable=True),
        sa.Column("phone_encrypted", sa.String(length=255), nullable=True),
        sa.Column("language", sa.String(length=5), nullable=False, server_default="ta"),
        sa.Column(
            "theme_preference",
            sa.String(length=10),
            nullable=False,
            server_default="system",
        ),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.Column("taluk", sa.String(length=100), nullable=True),
        sa.Column("village", sa.String(length=100), nullable=True),
        sa.Column("location_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_consent_given", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="farmer"),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_hash"),
    )
    op.create_index(op.f("ix_farmers_language"), "farmers", ["language"], unique=False)
    op.create_index(
        "idx_farmer_lang_theme",
        "farmers",
        ["language", "theme_preference"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("farmers")
    op.drop_table("locations")
