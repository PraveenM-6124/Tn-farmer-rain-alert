# Notification Engine Specification

## Multichannel Delivery Pipeline
1. **SMS (TRAI DLT)**: High reliability fallback; strict 70-character UCS-2 segment accounting for Tamil.
2. **WhatsApp Business API**: Rich templates with actionable quick-reply buttons and lower delivery friction.
3. **Web Push**: In-browser notifications via Service Worker (VAPID).

## Delivery Lifecycle & Idempotency
- Each alert receives an `idempotency_key` based on `farmer_id:event_window:alert_type`.
- State machine: `QUEUED -> SENT -> DELIVERED -> FAILED -> RETRIED -> DEAD_LETTER`.
- Quiet hours (default 21:00 to 06:00 IST) prevent night disturbances, overridden only by severe weather emergencies.
