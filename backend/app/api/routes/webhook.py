"""O&G Agentic Canvas - Webhook Alert Receiver Route."""

from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.logging_config import get_logger

logger = get_logger("webhook_api")
router = APIRouter(prefix="/webhook", tags=["Webhook"])


class WebhookPayload(BaseModel):
    event: str | None = Field(default=None, description="Event name or type")
    event_type: str | None = Field(default=None, description="Alternative event type")
    execution_id: str | None = None
    campaign_id: str | None = None
    campaign_name: str | None = None
    status: str | None = None
    score: float | None = None
    details: Dict[str, Any] | None = None
    execution: Dict[str, Any] | None = None


@router.post("/alert", status_code=status.HTTP_200_OK)
async def receive_webhook_alert(payload: WebhookPayload):
    """Receive automated lifecycle alerts from n8n or internal webhook triggers."""
    event_name = payload.event or payload.event_type or "unknown_event"
    logger.info(
        "webhook_alert_received",
        alert_name=event_name,
        execution_id=payload.execution_id or (payload.execution.get("id") if payload.execution else None),
        status=payload.status,
    )

    return {
        "status": "received",
        "event": event_name,
        "processed": True,
    }
