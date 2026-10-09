"""Background scheduler service executing weather sync and alert jobs."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.core.logging import logger
from backend.app.models.admin_audit import SchedulerRun
from backend.app.models.farmer import Farmer
from backend.app.services.alert_service import generate_farmer_alert
from backend.app.services.notifications.notification_service import notification_service
from backend.app.services.rain_analysis import analyze_72h_rain_forecast
from backend.app.services.weather.weather_service import weather_service


class SchedulerService:
    """Orchestrates scheduled cron jobs and records run metrics to database."""

    def __init__(self) -> None:
        self.is_running = False

    async def run_weather_sync_and_alert_job(self) -> int:
        """Run daily weather analysis and alert dispatch across registered farmers."""
        started_at = datetime.now(UTC)
        processed_count = 0
        error_msg = None

        db: Session = SessionLocal()
        try:
            farmers = (
                db.execute(select(Farmer).where(Farmer.is_active.is_(True), Farmer.is_deleted.is_(False)))
                .scalars()
                .all()
            )
            for farmer in farmers:
                lat = farmer.latitude or 12.9229
                lon = farmer.longitude or 79.3329

                try:
                    forecast = await weather_service.get_forecast(lat, lon)
                    hourly_dicts = [p.model_dump() for p in forecast.hourly]
                    assessment = analyze_72h_rain_forecast(hourly_dicts, imd_warning_level=forecast.imd_warning_level)

                    if assessment.get("should_alert"):
                        alert = generate_farmer_alert(db, farmer, assessment, alert_type="24h")
                        if alert:
                            await notification_service.dispatch_alert(db, alert, farmer)
                    processed_count += 1
                except Exception as farmer_err:
                    logger.warning("Error processing alerts for farmer %s: %s", str(farmer.id), str(farmer_err))

            # Record run telemetry
            run = SchedulerRun(
                job_name="WEATHER_SYNC_AND_ALERTS",
                status="success",
                items_processed=processed_count,
                started_at=started_at,
                finished_at=datetime.now(UTC),
            )
            db.add(run)
            db.commit()
            logger.info("Scheduler completed WEATHER_SYNC_AND_ALERTS for %d farmers.", processed_count)
            return processed_count
        except Exception as exc:
            logger.error("Scheduler job failed: %s", str(exc))
            error_msg = str(exc)
            run = SchedulerRun(
                job_name="WEATHER_SYNC_AND_ALERTS",
                status="failed",
                items_processed=processed_count,
                error_message=error_msg,
                started_at=started_at,
                finished_at=datetime.now(UTC),
            )
            db.add(run)
            db.commit()
            return 0
        finally:
            db.close()


scheduler_service = SchedulerService()
