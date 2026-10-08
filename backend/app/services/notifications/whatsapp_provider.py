"""WhatsApp Business Platform provider stub.

TODO (Phase 8):
Meta WhatsApp Cloud API with pre-approved templates in Tamil and English.
"""

from backend.app.services.notifications.base import BaseNotificationProvider


class WhatsAppProvider(BaseNotificationProvider):
    async def send_message(self, recipient: str, message: str) -> dict:
        raise NotImplementedError("WhatsAppProvider will be implemented in Phase 8")
