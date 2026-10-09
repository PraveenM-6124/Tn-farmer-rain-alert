"""Security, cryptographic functions, OTP hashing, and JWT handling."""

import base64
import hashlib
import hmac
import re
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

from backend.app.core.config import settings

# Indian mobile regex (starts with 6-9, followed by 9 digits)
INDIAN_MOBILE_REGEX = re.compile(r"^(?:\+91|91|0)?[6-9]\d{9}$")


def normalize_indian_phone(phone: str) -> str:
    """Normalize input phone to E.164 format (+91XXXXXXXXXX).

    Raises ValueError if the phone number is invalid.
    """
    clean = re.sub(r"[\s\-\(\)]", "", phone.strip())
    if not INDIAN_MOBILE_REGEX.match(clean):
        raise ValueError("Invalid Indian mobile number. Must be 10 digits starting with 6-9.")

    digits = re.sub(r"\D", "", clean)
    if digits.startswith("91") and len(digits) == 12:
        return f"+{digits}"
    elif digits.startswith("0") and len(digits) == 11:
        return f"+91{digits[1:]}"
    elif len(digits) == 10:
        return f"+91{digits}"
    return f"+91{digits[-10:]}"


def hash_phone(normalized_phone: str) -> str:
    """Hash phone number with secret salt for indexed lookup without plaintext PII."""
    salted = f"{settings.SECRET_KEY}:{normalized_phone}"
    return hashlib.sha256(salted.encode("utf-8")).hexdigest()


def mask_phone(phone: str) -> str:
    """Mask phone number for safe display (+91 ******1234)."""
    try:
        norm = normalize_indian_phone(phone)
        return f"{norm[:3]} ******{norm[-4:]}"
    except Exception:
        if len(phone) >= 4:
            return f"******{phone[-4:]}"
        return "******"


def encrypt_phone(normalized_phone: str) -> str:
    """Obfuscate/encrypt phone number using simple key-based XOR-base64."""
    key = settings.SECRET_KEY.encode("utf-8")
    data = normalized_phone.encode("utf-8")
    encrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
    return base64.urlsafe_b64encode(encrypted).decode("ascii")


def decrypt_phone(encrypted_phone: str) -> str:
    """Decrypt obfuscated phone number."""
    key = settings.SECRET_KEY.encode("utf-8")
    data = base64.urlsafe_b64decode(encrypted_phone.encode("ascii"))
    decrypted = bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])
    return decrypted.decode("utf-8")


def generate_otp() -> str:
    """Generate a cryptographically secure 6-digit OTP."""
    return "".join(str(secrets.randbelow(10)) for _ in range(6))


def hash_otp(otp: str, salt: str) -> str:
    """Hash OTP using SHA-256 and unique request salt."""
    return hashlib.sha256(f"{salt}:{otp}".encode()).hexdigest()


def verify_otp_hash(input_otp: str, stored_hash: str, salt: str) -> bool:
    """Constant-time verification of submitted OTP."""
    computed_hash = hash_otp(input_otp, salt)
    return secrets.compare_digest(computed_hash, stored_hash)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """Generate a lightweight HMAC-signed access token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=60))
    to_encode["exp"] = int(expire.timestamp())
    payload_json = (
        f'{{"sub":"{to_encode.get("sub", "")}","role":"{to_encode.get("role", "farmer")}","exp":{to_encode["exp"]}}}'
    )
    b64_payload = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("ascii").rstrip("=")
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        b64_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return f"{b64_payload}.{signature}"


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and verify token HMAC signature."""
    try:
        parts = token.split(".")
        if len(parts) != 2:
            return None
        b64_payload, signature = parts
        expected_sig = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            b64_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        if not secrets.compare_digest(signature, expected_sig):
            return None

        # Add base64 padding if needed
        padding = 4 - (len(b64_payload) % 4)
        if padding != 4:
            b64_payload += "=" * padding

        import json

        payload = json.loads(base64.urlsafe_b64decode(b64_payload.encode("ascii")).decode("utf-8"))
        if payload.get("exp", 0) < int(datetime.now(UTC).timestamp()):
            return None  # Expired
        return payload
    except Exception:
        return None
