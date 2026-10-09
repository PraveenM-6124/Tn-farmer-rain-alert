"""Authentication API routes: Phone normalization, 6-digit OTP, and JWT handling."""

import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.config import settings
from backend.app.core.database import get_db
from backend.app.core.rate_limit import is_rate_limited, reset_rate_limit
from backend.app.core.security import (
    create_access_token,
    decode_access_token,
    encrypt_phone,
    generate_otp,
    hash_otp,
    hash_phone,
    mask_phone,
    normalize_indian_phone,
    verify_otp_hash,
)
from backend.app.models.farmer import Farmer
from backend.app.models.notification import OTPRequest
from backend.app.schemas.auth import (
    SendOTPRequest,
    SendOTPResponse,
    TokenResponse,
    VerifyOTPRequest,
)
from backend.app.services.notifications.mock_sms import MockSMSProvider

router = APIRouter(prefix="/auth", tags=["Auth"])


def get_current_farmer(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> Farmer:
    """Dependency extracting and verifying the authenticated farmer from cookie or Bearer header."""
    auth_header = request.headers.get("Authorization")
    token = None
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    if not token:
        token = request.cookies.get("tn_farmer_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    payload = decode_access_token(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    try:
        farmer_id = uuid.UUID(payload["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid farmer identifier")

    farmer = db.execute(select(Farmer).where(Farmer.id == farmer_id, Farmer.is_deleted.is_(False))).scalar_one_or_none()
    if not farmer or not farmer.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Farmer account not active")

    return farmer


@router.post("/send-otp", response_model=SendOTPResponse, summary="Send 6-digit OTP")
async def send_otp(
    payload: SendOTPRequest,
    db: Annotated[Session, Depends(get_db)],
) -> SendOTPResponse:
    """Validate Indian phone, rate-limit requests, and send secure 6-digit OTP."""
    try:
        norm_phone = normalize_indian_phone(payload.phone)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    # Rate limiting: max 3 requests per 5 minutes per phone
    if is_rate_limited(f"otp:{norm_phone}", max_attempts=3, window_seconds=300):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many OTP requests. Please wait 5 minutes before retrying.",
        )

    phone_h = hash_phone(norm_phone)
    otp_code = generate_otp()
    salt = secrets.token_hex(16)
    otp_h = hash_otp(otp_code, salt)
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=5)

    otp_record = OTPRequest(
        phone_hash=phone_h,
        otp_hash=otp_h,
        salt=salt,
        attempts=0,
        expires_at=expires_at,
        is_used=False,
    )
    db.add(otp_record)
    db.commit()

    # Dispatch via Mock SMS provider
    sms_provider = MockSMSProvider()
    await sms_provider.send_message(
        recipient=norm_phone,
        message=f"FARMER RAIN ALERT: Your verification code is {otp_code}. Valid for 5 minutes. Do not share with anyone.",
    )

    hint = otp_code if settings.DEBUG or settings.ENV == "development" else None

    return SendOTPResponse(
        success=True,
        phone_masked=mask_phone(norm_phone),
        message="OTP sent successfully to your mobile number",
        is_mock=True,
        mock_otp_hint=hint,
    )


@router.post("/verify-otp", response_model=TokenResponse, summary="Verify OTP and issue session token")
async def verify_otp(
    payload: VerifyOTPRequest,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Verify 6-digit OTP, register or login farmer, and issue JWT."""
    try:
        norm_phone = normalize_indian_phone(payload.phone)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    phone_h = hash_phone(norm_phone)
    now = datetime.now(UTC)

    # Find most recent unused OTP for this phone
    otp_record = (
        db.execute(
            select(OTPRequest)
            .where(
                OTPRequest.phone_hash == phone_h,
                OTPRequest.is_used.is_(False),
                OTPRequest.expires_at > now,
            )
            .order_by(OTPRequest.created_at.desc())
        )
        .scalars()
        .first()
    )

    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active OTP found or OTP has expired. Please request a new code.",
        )

    # Brute-force protection: max 5 verify attempts per OTP
    if otp_record.attempts >= 5:
        otp_record.is_used = True
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many invalid attempts. This OTP has been invalidated.",
        )

    otp_record.attempts += 1
    if not verify_otp_hash(payload.otp, otp_record.otp_hash, otp_record.salt):
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP code. {5 - otp_record.attempts} attempts remaining.",
        )

    # Validated: mark OTP as used and reset rate limit
    otp_record.is_used = True
    reset_rate_limit(f"otp:{norm_phone}")

    # Check or create farmer account
    farmer = db.execute(select(Farmer).where(Farmer.phone_hash == phone_h)).scalar_one_or_none()
    is_new = False
    if not farmer:
        is_new = True
        farmer = Farmer(
            phone_hash=phone_h,
            phone_encrypted=encrypt_phone(norm_phone),
            language=settings.DEFAULT_LANGUAGE,
            theme_preference="light",
            is_active=True,
            is_consent_given=False,
            role="farmer",
        )
        db.add(farmer)
        db.commit()
        db.refresh(farmer)

    # Generate JWT access token
    access_token = create_access_token(
        data={"sub": str(farmer.id), "role": farmer.role},
        expires_delta=timedelta(days=7),
    )

    # Set persistent authentication cookie
    response.set_cookie(
        key="tn_farmer_token",
        value=access_token,
        max_age=7 * 86400,
        httponly=True,
        samesite="lax",
    )

    return TokenResponse(
        access_token=access_token,
        farmer_id=str(farmer.id),
        is_new_farmer=is_new,
        message="Login successful",
    )


@router.post("/logout", summary="Log out and clear session cookie")
def logout(response: Response) -> dict:
    """Clear session authentication cookie."""
    response.delete_cookie(key="tn_farmer_token")
    return {"success": True, "message": "Logged out successfully"}
