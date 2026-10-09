"""Rate limiting utilities for OTP requests and public API protection."""

from datetime import UTC, datetime

# In-memory storage for sliding window timestamps: key -> list of timestamp floats
_rate_limit_store: dict[str, list[float]] = {}


def is_rate_limited(key: str, max_attempts: int = 5, window_seconds: int = 300) -> bool:
    """Check if key has exceeded allowed attempts within the sliding window."""
    now = datetime.now(UTC).timestamp()
    history = _rate_limit_store.get(key, [])
    # Filter timestamps within window
    valid_history = [ts for ts in history if now - ts < window_seconds]
    _rate_limit_store[key] = valid_history

    if len(valid_history) >= max_attempts:
        return True

    valid_history.append(now)
    _rate_limit_store[key] = valid_history
    return False


def reset_rate_limit(key: str) -> None:
    """Reset rate limit history for a key."""
    _rate_limit_store.pop(key, None)
