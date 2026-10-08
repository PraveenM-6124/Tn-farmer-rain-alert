"""Authentication API routes stub.

TODO (Phase 2):
POST /auth/send-otp
POST /auth/verify-otp
POST /auth/refresh
"""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth (Phase 2)"])
