"""Health and readiness check response schemas."""

from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Response schema for liveness / health check."""

    status: str = Field(default="ok", examples=["ok"])
    app_name: str
    environment: str


class ReadinessCheckResponse(BaseModel):
    """Response schema for readiness check including database connectivity."""

    status: str = Field(examples=["ready"])
    database: str = Field(examples=["connected"])
    environment: str
