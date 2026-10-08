"""Rain alert model stub for farmer alerts and deduplication.

TODO (Phase 5):
Will define RainAlert:
- farmer_id, alert_type (24h, 12h, 3h, severe, change)
- rain_start, rain_end, rainfall_min_mm, rainfall_max_mm, probability, severity
- idempotency_key (unique constraint)
- message_en, message_ta
- delivery_status (queued, sent, delivered, failed)
"""
