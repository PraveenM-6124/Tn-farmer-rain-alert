"""Mock Web Push Provider stub.

TODO (Phase 6):
Simulates Web Push notifications for testing.
"""

from backend.app.services.notifications.base import BaseNotificationProvider


class MockPushProvider(BaseNotificationProvider):
    async def send_message(self, recipient: str, message: str) -> dict:
        return {"status": "success", "provider": "MOCK_PUSH", "id": "mock-push-id"}
