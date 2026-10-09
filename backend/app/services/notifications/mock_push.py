"""Mock Web Push provider tagged MOCK/DEMO."""

import uuid
from typing import Any

from backend.app.core.logging import logger
from backend.app.services.notifications.base import BaseNotificationProvider


class MockPushProvider(BaseNotificationProvider):
    """Simulates browser Web Push notification delivery tagged explicitly as DEMO/MOCK."""

    async def send_message(self, recipient: str, message: str, **kwargs: Any) -> dict[str, Any]:
        msg_id = f"mock-push-{uuid.uuid4().hex[:8]}"

        logger.info("[MOCK/DEMO PUSH] Dispatched push alert to endpoint: %s", recipient)

        return {
            "status": "delivered",
            "provider": "MOCK_PUSH (DEMO)",
            "provider_msg_id": msg_id,
            "cost_inr": 0.0,
            "is_mock": True,
        }
