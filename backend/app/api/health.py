"""Health and readiness check endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.logging import logger
from backend.app.schemas.health import HealthCheckResponse, ReadinessCheckResponse

router = APIRouter(tags=["Health"])


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Liveness check",
    description="Check if the FastAPI service is running.",
)
def get_health() -> HealthCheckResponse:
    """Return application liveness status."""
    return HealthCheckResponse(
        status="ok",
        app_name=settings.APP_NAME,
        environment=settings.ENV,
    )


@router.get(
    "/ready",
    response_model=ReadinessCheckResponse,
    summary="Readiness check",
    description="Check if the application and database are ready to serve requests.",
)
def get_readiness(
    db: Annotated[Session, Depends(get_db)],
) -> ReadinessCheckResponse:
    """Validate database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return ReadinessCheckResponse(
            status="ready",
            database="connected",
            environment=settings.ENV,
        )
    except SQLAlchemyError as exc:
        logger.error("Readiness check failed: %s", str(exc))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection unavailable",
        ) from exc
