"""SMS Provider stub (DLT registered).

TODO (Phase 8):
TRAI DLT entity, sender ID/header, content templates, UCS-2 segment tracking.
"""

from backend.app.services.notifications.base import BaseNotificationProvider


class SMSProvider(BaseNotificationProvider):
    async def send_message(self, recipient: str, message: str) -> dict:
        raise NotImplementedError("SMSProvider will be implemented in Phase 8")
