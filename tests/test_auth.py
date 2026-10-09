"""Tests for authentication, phone normalization, OTP lifecycle, and security utilities."""

import pytest

from backend.app.core.rate_limit import is_rate_limited, reset_rate_limit
from backend.app.core.security import (
    create_access_token,
    decode_access_token,
    generate_otp,
    hash_otp,
    mask_phone,
    normalize_indian_phone,
    verify_otp_hash,
)


def test_normalize_indian_phone_valid() -> None:
    """Test valid phone variations normalize to E.164 (+91...)."""
    assert normalize_indian_phone("+919876543210") == "+919876543210"
    assert normalize_indian_phone("9876543210") == "+919876543210"
    assert normalize_indian_phone("09876543210") == "+919876543210"
    assert normalize_indian_phone("+91 98765 43210") == "+919876543210"
    assert normalize_indian_phone("98765-43210") == "+919876543210"


def test_normalize_indian_phone_invalid() -> None:
    """Test invalid numbers raise ValueError."""
    with pytest.raises(ValueError):
        normalize_indian_phone("12345")  # Too short
    with pytest.raises(ValueError):
        normalize_indian_phone("5876543210")  # Invalid start digit (not 6-9)
    with pytest.raises(ValueError):
        normalize_indian_phone("abcd123456")  # Non-numeric


def test_mask_phone_pii() -> None:
    """Ensure phone masking conceals middle digits for DPDP compliance."""
    masked = mask_phone("+919876543210")
    assert "3210" in masked
    assert "***" in masked
    assert "9876543210" not in masked


def test_otp_generation_and_hashing() -> None:
    """Verify 6-digit OTP generation, salted SHA-256 hashing, and verification."""
    otp = generate_otp()
    assert len(otp) == 6
    assert otp.isdigit()

    salt = "random_salt_123"
    h = hash_otp(otp, salt)
    assert verify_otp_hash(otp, h, salt) is True
    assert verify_otp_hash("000000", h, salt) is False


def test_jwt_token_encode_decode() -> None:
    """Verify access token creation and decoding."""
    token = create_access_token({"sub": "test_farmer_uuid", "role": "farmer"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "test_farmer_uuid"
    assert payload["role"] == "farmer"


def test_sliding_window_rate_limiting() -> None:
    """Verify in-memory sliding window rate limiter prevents brute-force attempts."""
    key = "test_limiter_key"
    reset_rate_limit(key)

    # 3 attempts allowed
    assert is_rate_limited(key, max_attempts=3, window_seconds=60) is False
    assert is_rate_limited(key, max_attempts=3, window_seconds=60) is False
    assert is_rate_limited(key, max_attempts=3, window_seconds=60) is False
    # 4th attempt blocked
    assert is_rate_limited(key, max_attempts=3, window_seconds=60) is True

    reset_rate_limit(key)
    assert is_rate_limited(key, max_attempts=3, window_seconds=60) is False
