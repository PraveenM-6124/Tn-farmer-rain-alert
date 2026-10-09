"""Base notification interface and India-specific SMS segment counter."""

from abc import ABC, abstractmethod
from typing import Any


def calculate_sms_segments(message: str) -> tuple[int, str, float]:
    """Calculate SMS segment count and cost under TRAI regulations.

    Rules:
    - Standard GSM-7 (ASCII): 160 chars for 1 segment, 153 chars/part for multi-part.
    - Unicode UCS-2 (Tamil/non-ASCII): 70 chars for 1 segment, 67 chars/part for multi-part.
    - Base cost assumption: approx ₹0.15 per SMS segment.
    """
    is_unicode = any(ord(char) > 127 for char in message)
    encoding = "UCS-2 (Unicode)" if is_unicode else "GSM-7"
    char_count = len(message)

    if is_unicode:
        if char_count <= 70:
            segments = 1
        else:
            segments = (char_count + 66) // 67
    else:
        if char_count <= 160:
            segments = 1
        else:
            segments = (char_count + 152) // 153

    cost_inr = round(segments * 0.15, 2)
    return segments, encoding, cost_inr


class BaseNotificationProvider(ABC):
    """Abstract interface for notification dispatch."""

    @abstractmethod
    async def send_message(self, recipient: str, message: str, **kwargs: Any) -> dict[str, Any]:
        """Dispatch message to recipient and return delivery details."""
