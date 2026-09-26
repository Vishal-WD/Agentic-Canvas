"""O&G Agentic Canvas - Automated Webhook Alerts Service.

Dispatches asynchronous webhook notifications on key execution events:
execution_started, execution_completed, review_required, and execution_failed.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional
import httpx

from app.config import get_settings
from app.logging_config import get_logger

logger = get_logger("webhook_service")


class WebhookAlertService:
    """Service to deliver automated webhook alerts."""

    def __init__(self, webhook_url: Optional[str] = None):
        settings = get_settings()
        self.webhook_url = webhook_url or settings.webhook_alert_url

    async def send_alert(
        self,
        event_type: str,
        execution_id: uuid.UUID,
        campaign_id: uuid.UUID,
        campaign_name: str,
        status: str,
        score: Optional[float] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> bool:
        """Send an automated webhook alert payload."""
        if not self.webhook_url:
            logger.debug(
                "webhook_alert_skipped_no_url",
                event_type=event_type,
                execution_id=str(execution_id),
            )
            return False

        payload = {
            "event": f"ong.agentic_canvas.{event_type}",
            "execution_id": str(execution_id),
            "campaign_id": str(campaign_id),
            "campaign_name": campaign_name,
            "status": status,
            "compliance_score": score,
            "details": details or {},
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(self.webhook_url, json=payload)
                if response.is_success:
                    logger.info(
                        "webhook_alert_sent",
                        event_type=event_type,
                        execution_id=str(execution_id),
                        status_code=response.status_code,
                    )
                    return True
                else:
                    logger.warning(
                        "webhook_alert_non_200",
                        event_type=event_type,
                        execution_id=str(execution_id),
                        status_code=response.status_code,
                    )
                    return False
        except Exception as e:
            logger.warning(
                "webhook_alert_failed",
                event_type=event_type,
                execution_id=str(execution_id),
                error=str(e),
            )
            return False
