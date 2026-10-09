"""Mock SMS provider simulating TRAI DLT delivery with MOCK/DEMO logging."""

import uuid
from typing import Any

from backend.app.core.logging import logger
from backend.app.services.notifications.base import (
    BaseNotificationProvider,
    calculate_sms_segments,
)


class MockSMSProvider(BaseNotificationProvider):
    """Simulates outbound SMS delivery tagged explicitly as DEMO/MOCK."""

    async def send_message(self, recipient: str, message: str, **kwargs: Any) -> dict[str, Any]:
        segments, encoding, cost = calculate_sms_segments(message)
        msg_id = f"mock-sms-{uuid.uuid4().hex[:8]}"

        logger.info(
            "[MOCK/DEMO SMS] Sent to %s (%d chars, %d segments, %s, est. cost: ₹%.2f)\nContent:\n%s",
            recipient,
            len(message),
            segments,
            encoding,
            cost,
            message,
        )

        return {
            "status": "delivered",
            "provider": "MOCK_SMS (DEMO)",
            "provider_msg_id": msg_id,
            "segments": segments,
            "encoding": encoding,
            "cost_inr": cost,
            "is_mock": True,
        }
