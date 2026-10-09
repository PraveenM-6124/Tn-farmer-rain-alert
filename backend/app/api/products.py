"""Agricultural marketplace products and buyer enquiry API endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.auth import get_current_farmer
from backend.app.core.database import get_db
from backend.app.core.rate_limit import is_rate_limited
from backend.app.core.security import mask_phone
from backend.app.models.farmer import Farmer
from backend.app.models.product import Product, ProductEnquiry
from backend.app.schemas.product import (
    EnquiryCreate,
    EnquiryResponse,
    ProductCreate,
    ProductResponse,
)

router = APIRouter(prefix="/products", tags=["Marketplace"])


@router.get("", response_model=list[ProductResponse], summary="Search and list marketplace products")
def list_products(
    db: Annotated[Session, Depends(get_db)],
    category: str | None = Query(default=None),
    district: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[ProductResponse]:
    """Retrieve active marketplace listings with optional category and district filters."""
    query = select(Product).where(Product.is_active.is_(True), Product.is_reported.is_(False))

    if category:
        query = query.where(Product.category == category.lower())
    if district:
        query = query.where(Product.district == district)
    if search:
        search_filter = f"%{search}%"
        query = query.where(Product.name_en.ilike(search_filter) | Product.name_ta.ilike(search_filter))

    query = query.order_by(Product.created_at.desc()).limit(limit)
    products = db.execute(query).scalars().all()

    return [
        ProductResponse(
            id=p.id,
            farmer_id=p.farmer_id,
            name_en=p.name_en,
            name_ta=p.name_ta,
            category=p.category,
            quantity=p.quantity,
            unit=p.unit,
            price_inr=p.price_inr,
            description=p.description,
            district=p.district,
            taluk=p.taluk,
            village=p.village,
            is_active=p.is_active,
            created_at=p.created_at,
        )
        for p in products
    ]


@router.post("", response_model=ProductResponse, summary="List a new product")
def create_product(
    payload: ProductCreate,
    farmer: Annotated[Farmer, Depends(get_current_farmer)],
    db: Annotated[Session, Depends(get_db)],
) -> ProductResponse:
    """Create a new product listing for the logged-in farmer."""
    product = Product(
        farmer_id=farmer.id,
        name_en=payload.name_en,
        name_ta=payload.name_ta,
        category=payload.category.lower(),
        quantity=payload.quantity,
        unit=payload.unit,
        price_inr=payload.price_inr,
        description=payload.description,
        district=payload.district or farmer.district or "Ranipet",
        taluk=payload.taluk or farmer.taluk or "Arakkonam",
        village=payload.village or farmer.village or "Thakkolam",
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return ProductResponse(
        id=product.id,
        farmer_id=product.farmer_id,
        name_en=product.name_en,
        name_ta=product.name_ta,
        category=product.category,
        quantity=product.quantity,
        unit=product.unit,
        price_inr=product.price_inr,
        description=product.description,
        district=product.district,
        taluk=product.taluk,
        village=product.village,
        is_active=product.is_active,
        created_at=product.created_at,
    )


@router.get("/{product_id}", response_model=ProductResponse, summary="Get single product details")
def get_product(
    product_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
) -> ProductResponse:
    """Retrieve details for a single product listing."""
    product = db.execute(
        select(Product).where(Product.id == product_id, Product.is_active.is_(True))
    ).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return ProductResponse(
        id=product.id,
        farmer_id=product.farmer_id,
        name_en=product.name_en,
        name_ta=product.name_ta,
        category=product.category,
        quantity=product.quantity,
        unit=product.unit,
        price_inr=product.price_inr,
        description=product.description,
        district=product.district,
        taluk=product.taluk,
        village=product.village,
        is_active=product.is_active,
        created_at=product.created_at,
    )


@router.post("/{product_id}/enquire", response_model=EnquiryResponse, summary="Send enquiry for product")
def send_enquiry(
    product_id: uuid.UUID,
    payload: EnquiryCreate,
    db: Annotated[Session, Depends(get_db)],
) -> EnquiryResponse:
    """Submit an in-app enquiry to farmer with rate limiting to prevent scraping."""
    # Rate limit: max 5 enquiries per 10 minutes per buyer phone
    if is_rate_limited(f"enquiry:{payload.buyer_phone}", max_attempts=5, window_seconds=600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many enquiries sent. Please wait a few minutes before submitting another.",
        )

    product = db.execute(select(Product).where(Product.id == product_id)).scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    enquiry = ProductEnquiry(
        product_id=product.id,
        buyer_name=payload.buyer_name,
        buyer_phone_masked=mask_phone(payload.buyer_phone),
        message=payload.message,
    )
    db.add(enquiry)
    db.commit()

    return EnquiryResponse(
        success=True,
        message="Enquiry forwarded to farmer. The farmer will contact you directly.",
    )
