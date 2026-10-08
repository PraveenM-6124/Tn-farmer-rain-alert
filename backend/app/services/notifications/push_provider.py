"""Web Push provider stub.

TODO (Phase 6):
VAPID Web Push provider with service worker push notification delivery.
"""

from backend.app.services.notifications.base import BaseNotificationProvider


class PushProvider(BaseNotificationProvider):
    async def send_message(self, recipient: str, message: str) -> dict:
        raise NotImplementedError("PushProvider will be implemented in Phase 6")
