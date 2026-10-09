"""Admin audit logging and scheduler telemetry models."""

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.core.database import Base
from backend.app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class AdminAuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Audit log for all administrative actions (viewing farmer contacts, unmasking, moderating)."""

    __tablename__ = "admin_audit_logs"

    admin_username: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # UNMASK_PHONE, MODERATE_PRODUCT, etc.
    target_type: Mapped[str] = mapped_column(String(50), nullable=False)  # farmer, product, alert
    target_id: Mapped[str] = mapped_column(String(50), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)


class SchedulerRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Execution telemetry for scheduled background jobs."""

    __tablename__ = "scheduler_runs"

    job_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), default="running", nullable=False)  # running, success, failed
    items_processed: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
