"""Products API routes stub.

TODO (Phase 10):
GET /products
POST /products
GET /products/{id}
PUT /products/{id}
DELETE /products/{id}
"""

from fastapi import APIRouter

router = APIRouter(prefix="/products", tags=["Products (Phase 10)"])
