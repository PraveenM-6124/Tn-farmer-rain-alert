"""Mock WhatsApp Cloud API provider tagged MOCK/DEMO."""

import uuid
from typing import Any

from backend.app.core.logging import logger
from backend.app.services.notifications.base import BaseNotificationProvider


class MockWhatsAppProvider(BaseNotificationProvider):
    """Simulates WhatsApp Business Cloud API delivery tagged explicitly as DEMO/MOCK."""

    async def send_message(self, recipient: str, message: str, **kwargs: Any) -> dict[str, Any]:
        msg_id = f"mock-wamid-{uuid.uuid4().hex[:12]}"
        cost = 0.40  # Standard Meta utility message rate in India approx ₹0.40

        logger.info(
            "[MOCK/DEMO WHATSAPP] Delivered template to %s (est. cost: ₹%.2f)\nMessage:\n%s",
            recipient,
            cost,
            message,
        )

        return {
            "status": "delivered",
            "provider": "MOCK_WHATSAPP (DEMO)",
            "provider_msg_id": msg_id,
            "cost_inr": cost,
            "is_mock": True,
        }
