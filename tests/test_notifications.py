"""Tests for notification pipeline, TRAI UCS-2 segment calculation, and mock providers."""

import pytest

from backend.app.services.notifications.base import calculate_sms_segments
from backend.app.services.notifications.mock_push import MockPushProvider
from backend.app.services.notifications.mock_sms import MockSMSProvider
from backend.app.services.notifications.mock_whatsapp import MockWhatsAppProvider


def test_calculate_sms_segments_gsm7() -> None:
    """Verify ASCII SMS segment calculation."""
    msg = "Rain alert: 20-30 mm expected today. Open field drainage."
    segments, encoding, cost = calculate_sms_segments(msg)
    assert segments == 1
    assert encoding == "GSM-7"
    assert cost == 0.15


def test_calculate_sms_segments_unicode_tamil() -> None:
    """Verify Tamil Unicode UCS-2 segment calculation (70 chars per segment)."""
    short_ta = "மழை எச்சரிக்கை: 20 மி.மீ மழை வாய்ப்பு."
    segments, encoding, cost = calculate_sms_segments(short_ta)
    assert segments == 1
    assert "UCS-2" in encoding
    assert cost == 0.15

    long_ta = "மழை எச்சரிக்கை: இன்று மாலை 2 மணி முதல் 6 மணி வரை மிதமான மழை பெய்ய வாய்ப்புள்ளது. வயல் வடிகால் வசதியை சரிசெய்து கொள்ளவும்."
    segments_long, encoding_long, cost_long = calculate_sms_segments(long_ta)
    assert segments_long >= 2
    assert "UCS-2" in encoding_long
    assert cost_long > 0.15


@pytest.mark.asyncio
async def test_mock_sms_provider() -> None:
    """Verify mock SMS provider dispatch."""
    provider = MockSMSProvider()
    res = await provider.send_message(recipient="+919876543210", message="Test alert")
    assert res["status"] == "delivered"
    assert "MOCK" in res["provider"]
    assert "provider_msg_id" in res


@pytest.mark.asyncio
async def test_mock_whatsapp_provider() -> None:
    """Verify mock WhatsApp provider dispatch."""
    provider = MockWhatsAppProvider()
    res = await provider.send_message(recipient="+919876543210", message="Test whatsapp")
    assert res["status"] == "delivered"
    assert "MOCK" in res["provider"]


@pytest.mark.asyncio
async def test_mock_push_provider() -> None:
    """Verify mock web push provider dispatch."""
    provider = MockPushProvider()
    res = await provider.send_message(recipient="device_token_xyz", message="Rain starting")
    assert res["status"] == "delivered"
    assert "MOCK" in res["provider"]
