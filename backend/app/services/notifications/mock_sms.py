"""Mock SMS Provider stub.

TODO (Phase 2 & Phase 6):
Logs SMS messages to console with MOCK/DEMO tag when ENV=development.
"""

from backend.app.services.notifications.base import BaseNotificationProvider


class MockSMSProvider(BaseNotificationProvider):
    async def send_message(self, recipient: str, message: str) -> dict:
        return {"status": "success", "provider": "MOCK_SMS", "id": "mock-sms-id"}
