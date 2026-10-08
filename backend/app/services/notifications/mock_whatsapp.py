"""Mock WhatsApp Provider stub.

TODO (Phase 6):
Simulates WhatsApp message delivery with MOCK/DEMO log.
"""

from backend.app.services.notifications.base import BaseNotificationProvider


class MockWhatsAppProvider(BaseNotificationProvider):
    async def send_message(self, recipient: str, message: str) -> dict:
        return {"status": "success", "provider": "MOCK_WHATSAPP", "id": "mock-wa-id"}
