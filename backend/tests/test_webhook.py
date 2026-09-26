"""O&G Agentic Canvas - Webhook Alert Unit Tests."""

import uuid
import pytest
from app.services.webhook_service import WebhookAlertService


@pytest.mark.asyncio
async def test_webhook_alert_skipped_without_url():
    service = WebhookAlertService(webhook_url=None)
    sent = await service.send_alert(
        event_type="execution_started",
        execution_id=uuid.uuid4(),
        campaign_id=uuid.uuid4(),
        campaign_name="Test Campaign",
        status="running",
    )
    assert sent is False


@pytest.mark.asyncio
async def test_webhook_alert_graceful_on_connection_error():
    # Attempting to call an unreachable localhost port should fail gracefully without crashing
    service = WebhookAlertService(webhook_url="http://127.0.0.1:59999/webhook")
    sent = await service.send_alert(
        event_type="execution_completed",
        execution_id=uuid.uuid4(),
        campaign_id=uuid.uuid4(),
        campaign_name="Test Campaign",
        status="approved",
        score=95.0,
    )
    assert sent is False
