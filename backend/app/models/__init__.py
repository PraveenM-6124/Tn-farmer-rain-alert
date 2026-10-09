"""SQLAlchemy models package exporting all entities."""

from backend.app.core.database import Base
from backend.app.models.admin_audit import AdminAuditLog, SchedulerRun
from backend.app.models.alert import RainAlert, RainAssessment
from backend.app.models.base import TimestampMixin, UUIDPrimaryKeyMixin
from backend.app.models.crop import Crop
from backend.app.models.farmer import Farmer
from backend.app.models.location import Location
from backend.app.models.notification import (
    Notification,
    NotificationPreference,
    OTPRequest,
)
from backend.app.models.product import Product, ProductEnquiry
from backend.app.models.weather import WeatherForecast, WeatherObservation

__all__ = [
    "AdminAuditLog",
    "Base",
    "Crop",
    "Farmer",
    "Location",
    "Notification",
    "NotificationPreference",
    "OTPRequest",
    "Product",
    "ProductEnquiry",
    "RainAlert",
    "RainAssessment",
    "SchedulerRun",
    "TimestampMixin",
    "UUIDPrimaryKeyMixin",
    "WeatherForecast",
    "WeatherObservation",
]
