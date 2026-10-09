"""Pydantic schemas for authentication and OTP verification."""

from pydantic import BaseModel, Field


class SendOTPRequest(BaseModel):
    """Schema for requesting a login/registration OTP."""

    phone: str = Field(..., description="10-digit Indian mobile number")


class SendOTPResponse(BaseModel):
    """Response returning OTP dispatch confirmation."""

    success: bool
    phone_masked: str
    message: str
    is_mock: bool = False
    mock_otp_hint: str | None = None  # Returned only in development mode for easy testing


class VerifyOTPRequest(BaseModel):
    """Schema for verifying submitted OTP."""

    phone: str = Field(..., description="10-digit Indian mobile number")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")


class TokenResponse(BaseModel):
    """JWT token response for authenticated sessions."""

    access_token: str
    token_type: str = "bearer"
    farmer_id: str
    is_new_farmer: bool
    message: str
