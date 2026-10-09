"""Schemas for marketplace products and masked enquiries."""

import uuid
from datetime import datetime

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name_en: str
    name_ta: str
    category: str
    quantity: float
    unit: str = "kg"
    price_inr: float
    description: str | None = None
    district: str
    taluk: str | None = None
    village: str | None = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    farmer_id: uuid.UUID
    name_en: str
    name_ta: str
    category: str
    quantity: float
    unit: str
    price_inr: float
    description: str | None = None
    district: str
    taluk: str | None = None
    village: str | None = None
    is_active: bool
    created_at: datetime


class EnquiryCreate(BaseModel):
    buyer_name: str
    buyer_phone: str
    message: str


class EnquiryResponse(BaseModel):
    success: bool
    message: str
