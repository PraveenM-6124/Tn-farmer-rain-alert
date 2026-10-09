"""Notification orchestration service dispatching alerts across preferred channels."""

from datetime import UTC, datetime

from sqlalchemy.orm import Session

from backend.app.core.logging import logger
from backend.app.core.security import decrypt_phone, mask_phone
from backend.app.models.alert import RainAlert
from backend.app.models.farmer import Farmer
from backend.app.models.notification import Notification
from backend.app.services.notifications.mock_push import MockPushProvider
from backend.app.services.notifications.mock_sms import MockSMSProvider
from backend.app.services.notifications.mock_whatsapp import MockWhatsAppProvider


class NotificationService:
    """Dispatches alerts to farmers with channel preferences, fallback order, and delivery auditing."""

    def __init__(self) -> None:
        self.sms_provider = MockSMSProvider()
        self.whatsapp_provider = MockWhatsAppProvider()
        self.push_provider = MockPushProvider()

    async def dispatch_alert(
        self,
        db: Session,
        alert: RainAlert,
        farmer: Farmer,
    ) -> Notification:
        """Deliver alert to farmer via preferred channel with WhatsApp -> SMS fallback."""
        # Determine language-specific message
        message = alert.message_ta if farmer.language == "ta" else alert.message_en

        # Decrypt farmer phone or use masked representation
        phone = "+919876543210"
        if farmer.phone_encrypted:
            try:
                phone = decrypt_phone(farmer.phone_encrypted)
            except Exception:
                phone = "+919876543210"

        masked_recipient = mask_phone(phone)

        # Check preferred channels
        channels_str = "whatsapp,sms"
        if farmer.notification_preferences and farmer.notification_preferences.channels:
            channels_str = farmer.notification_preferences.channels.lower()

        delivery_result = None
        chosen_channel = "whatsapp"

        # 1. Try WhatsApp if preferred
        if "whatsapp" in channels_str:
            try:
                delivery_result = await self.whatsapp_provider.send_message(
                    recipient=phone,
                    message=message,
                )
                chosen_channel = "whatsapp"
            except Exception as exc:
                logger.warning("WhatsApp delivery failed: %s. Falling back to SMS.", str(exc))

        # 2. Fallback to SMS
        if not delivery_result or delivery_result.get("status") != "delivered":
            delivery_result = await self.sms_provider.send_message(
                recipient=phone,
                message=message,
            )
            chosen_channel = "sms"

        status = delivery_result.get("status", "sent")
        cost = delivery_result.get("cost_inr", 0.15)
        provider_msg_id = delivery_result.get("provider_msg_id")

        # Record notification in database
        notification = Notification(
            alert_id=alert.id,
            farmer_id=farmer.id,
            channel=chosen_channel,
            recipient=masked_recipient,
            message=message,
            provider_msg_id=provider_msg_id,
            status=status,
            cost_inr=cost,
            retry_count=0,
            sent_at=datetime.now(UTC),
        )
        db.add(notification)

        # Update alert status
        alert.delivery_status = status
        db.commit()
        db.refresh(notification)

        logger.info(
            "Notification %s logged for Alert %s via %s (status: %s)",
            str(notification.id),
            str(alert.id),
            chosen_channel,
            status,
        )
        return notification


notification_service = NotificationService()
