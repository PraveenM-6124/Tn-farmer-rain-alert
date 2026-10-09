"""Admin dashboard, monitoring, audit logging, and moderation API endpoints."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.security import decrypt_phone, mask_phone
from backend.app.models.admin_audit import AdminAuditLog, SchedulerRun
from backend.app.models.alert import RainAlert
from backend.app.models.farmer import Farmer
from backend.app.models.notification import Notification
from backend.app.models.product import Product

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard", summary="Admin dashboard system overview metrics")
def get_admin_dashboard(db: Annotated[Session, Depends(get_db)]) -> dict[str, Any]:
    """Retrieve operational metrics across farmers, weather alerts, marketplace, and jobs."""
    total_farmers = db.execute(select(func.count(Farmer.id)).where(Farmer.is_deleted.is_(False))).scalar_one()
    total_alerts = db.execute(select(func.count(RainAlert.id))).scalar_one()
    total_products = db.execute(select(func.count(Product.id)).where(Product.is_active.is_(True))).scalar_one()

    # Delivery statistics
    notifications = db.execute(select(Notification)).scalars().all()
    delivered_count = sum(1 for n in notifications if n.status == "delivered")
    total_cost = sum(n.cost_inr for n in notifications)

    # Scheduler runs
    recent_runs = db.execute(select(SchedulerRun).order_by(SchedulerRun.started_at.desc()).limit(5)).scalars().all()

    return {
        "farmers": {
            "total": total_farmers,
            "active": total_farmers,
        },
        "alerts": {
            "total_generated": total_alerts,
            "delivered": delivered_count,
            "success_rate_percent": round((delivered_count / len(notifications) * 100), 1) if notifications else 100.0,
            "total_telecom_cost_inr": round(total_cost, 2),
        },
        "marketplace": {
            "active_listings": total_products,
        },
        "scheduler_status": "healthy",
        "recent_job_runs": [
            {
                "job_name": r.job_name,
                "status": r.status,
                "items": r.items_processed,
                "started_at": r.started_at.isoformat(),
            }
            for r in recent_runs
        ],
    }


@router.get("/farmers", summary="List registered farmers (masked PII by default)")
def list_farmers(
    db: Annotated[Session, Depends(get_db)],
    limit: int = Query(default=50, ge=1, le=100),
) -> list[dict]:
    """List registered farmers with masked mobile numbers for privacy compliance."""
    farmers = (
        db.execute(select(Farmer).where(Farmer.is_deleted.is_(False)).order_by(Farmer.created_at.desc()).limit(limit))
        .scalars()
        .all()
    )

    # Log audit entry
    audit = AdminAuditLog(
        admin_username="admin_user",
        action="VIEW_FARMER_LIST",
        target_type="farmer",
        target_id="bulk",
        details=f"Viewed {len(farmers)} farmer records",
    )
    db.add(audit)
    db.commit()

    return [
        {
            "id": str(f.id),
            "name": f.name or "Farmer",
            "phone_masked": mask_phone("+919876543210")
            if not f.phone_encrypted
            else mask_phone(decrypt_phone(f.phone_encrypted)),
            "district": f.district,
            "taluk": f.taluk,
            "village": f.village,
            "language": f.language,
            "crop_count": len(f.crops),
            "created_at": f.created_at.isoformat(),
        }
        for f in farmers
    ]


@router.post("/moderate-product/{product_id}", summary="Takedown / moderate marketplace listing")
def moderate_product(
    product_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
) -> dict:
    """Takedown reported product and create audit log."""
    product = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    product.is_active = False
    product.is_reported = True

    audit = AdminAuditLog(
        admin_username="admin_user",
        action="MODERATE_TAKEDOWN",
        target_type="product",
        target_id=str(product.id),
        details=f"Product '{product.name_en}' deactivated by admin",
    )
    db.add(audit)
    db.commit()

    return {"success": True, "message": f"Product {product_id} taken down successfully"}
