"""O&G Agentic Canvas - Execution Service Layer."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AgentRun,
    Campaign,
    CampaignStatus,
    Execution,
    ExecutionEvent,
    ExecutionStatus,
    GeneratedAsset,
    GuardrailResult,
)
from app.logging_config import get_logger

logger = get_logger("execution_service")


class ExecutionService:
    """Service layer for execution operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_execution(
        self,
        campaign_id: uuid.UUID,
        idempotency_key: Optional[str] = None,
    ) -> Execution:
        """Create a new execution, respecting idempotency."""
        # Check for existing execution with same idempotency key
        if idempotency_key:
            result = await self.db.execute(
                select(Execution).where(Execution.idempotency_key == idempotency_key)
            )
            existing = result.scalar_one_or_none()
            if existing:
                logger.info(
                    "execution_idempotency_hit",
                    execution_id=str(existing.id),
                    idempotency_key=idempotency_key,
                )
                return existing

        execution = Execution(
            campaign_id=campaign_id,
            status=ExecutionStatus.CREATED,
            current_state="created",
            idempotency_key=idempotency_key,
        )
        self.db.add(execution)
        await self.db.flush()
        await self.db.refresh(execution)

        # Create initial event
        await self.add_event(
            execution_id=execution.id,
            from_state=None,
            to_state="created",
            reason="Execution created",
            sequence=1,
        )

        logger.info(
            "execution_created",
            execution_id=str(execution.id),
            campaign_id=str(campaign_id),
        )
        return execution

    async def get_execution(self, execution_id: uuid.UUID) -> Optional[Execution]:
        """Get an execution by ID."""
        result = await self.db.execute(
            select(Execution).where(Execution.id == execution_id)
        )
        return result.scalar_one_or_none()

    async def update_execution_state(
        self,
        execution_id: uuid.UUID,
        new_status: ExecutionStatus,
        reason: str = "",
        final_score: Optional[float] = None,
        failure_reason: Optional[str] = None,
    ) -> Optional[Execution]:
        """Update execution state and log the transition event."""
        execution = await self.get_execution(execution_id)
        if not execution:
            return None

        old_state = execution.current_state
        execution.status = new_status
        execution.current_state = new_status.value

        if new_status in (ExecutionStatus.RUNNING,) and not execution.started_at:
            execution.started_at = datetime.now(timezone.utc)

        if new_status in (
            ExecutionStatus.APPROVED,
            ExecutionStatus.FAILED,
            ExecutionStatus.REVIEW_REQUIRED,
            ExecutionStatus.COMPLETED,
        ):
            execution.completed_at = datetime.now(timezone.utc)

        if final_score is not None:
            execution.final_score = final_score

        if failure_reason:
            execution.failure_reason = failure_reason

        # Get next sequence number
        event_count = len(execution.events) if execution.events else 0
        next_seq = event_count + 1

        await self.add_event(
            execution_id=execution_id,
            from_state=old_state,
            to_state=new_status.value,
            reason=reason,
            sequence=next_seq,
        )

        await self.db.commit()
        await self.db.refresh(execution)

        logger.info(
            "execution_state_changed",
            execution_id=str(execution_id),
            from_state=old_state,
            to_state=new_status.value,
            reason=reason,
        )
        return execution

    async def add_event(
        self,
        execution_id: uuid.UUID,
        from_state: Optional[str],
        to_state: str,
        reason: str,
        sequence: int,
    ) -> ExecutionEvent:
        """Add an execution event."""
        event = ExecutionEvent(
            execution_id=execution_id,
            from_state=from_state,
            to_state=to_state,
            reason=reason,
            sequence=sequence,
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_execution_events(self, execution_id: uuid.UUID) -> list[ExecutionEvent]:
        """Get all events for an execution, ordered by sequence."""
        result = await self.db.execute(
            select(ExecutionEvent)
            .where(ExecutionEvent.execution_id == execution_id)
            .order_by(ExecutionEvent.sequence)
        )
        return list(result.scalars().all())

    async def get_compliance_results(self, execution_id: uuid.UUID) -> list[GuardrailResult]:
        """Get guardrail results for an execution."""
        result = await self.db.execute(
            select(GuardrailResult)
            .where(GuardrailResult.execution_id == execution_id)
            .order_by(GuardrailResult.attempt_number)
        )
        return list(result.scalars().all())

    async def get_agent_runs(self, execution_id: uuid.UUID) -> list[AgentRun]:
        """Get agent runs for an execution."""
        result = await self.db.execute(
            select(AgentRun)
            .where(AgentRun.execution_id == execution_id)
            .order_by(AgentRun.created_at)
        )
        return list(result.scalars().all())

    async def get_generated_assets(self, campaign_id: uuid.UUID) -> list[GeneratedAsset]:
        """Get generated assets for a campaign."""
        result = await self.db.execute(
            select(GeneratedAsset)
            .where(GeneratedAsset.campaign_id == campaign_id)
            .order_by(GeneratedAsset.created_at)
        )
        return list(result.scalars().all())

    async def get_campaign_executions(self, campaign_id: uuid.UUID) -> list[Execution]:
        """Get all executions for a campaign, ordered by created_at descending."""
        result = await self.db.execute(
            select(Execution)
            .where(Execution.campaign_id == campaign_id)
            .order_by(Execution.started_at.desc().nullslast())
        )
        return list(result.scalars().all())

    async def increment_retry(self, execution_id: uuid.UUID) -> Optional[Execution]:
        """Increment the retry count for an execution."""
        execution = await self.get_execution(execution_id)
        if execution:
            execution.retry_count += 1
            await self.db.flush()
        return execution

    async def get_generated_asset(self, asset_id: uuid.UUID) -> Optional[GeneratedAsset]:
        """Get a single generated asset by ID."""
        result = await self.db.execute(
            select(GeneratedAsset).where(GeneratedAsset.id == asset_id)
        )
        return result.scalar_one_or_none()

    async def update_generated_asset(
        self,
        asset_id: uuid.UUID,
        content: Optional[dict] = None,
        status: Optional[str] = None,
    ) -> Optional[GeneratedAsset]:
        """Update a generated asset's content or status."""
        asset = await self.get_generated_asset(asset_id)
        if not asset:
            return None

        if content is not None:
            # Create a new dictionary or update in place to ensure SQLAlchemy detects change
            asset.content = dict(content)
        if status is not None:
            asset.status = status

        await self.db.flush()
        await self.db.refresh(asset)
        return asset

    async def delete_generated_asset(self, asset_id: uuid.UUID) -> bool:
        """Delete a single generated asset."""
        asset = await self.get_generated_asset(asset_id)
        if not asset:
            return False
        await self.db.delete(asset)
        await self.db.flush()
        return True

    async def delete_campaign_assets(self, campaign_id: uuid.UUID) -> int:
        """Delete all generated assets for a campaign."""
        result = await self.db.execute(
            delete(GeneratedAsset).where(GeneratedAsset.campaign_id == campaign_id)
        )
        await self.db.flush()
        return result.rowcount

    async def delete_execution_events(self, execution_id: uuid.UUID) -> int:
        """Delete all event logs for a specific execution."""
        result = await self.db.execute(
            delete(ExecutionEvent).where(ExecutionEvent.execution_id == execution_id)
        )
        await self.db.flush()
        return result.rowcount

    async def delete_campaign_logs(self, campaign_id: uuid.UUID) -> int:
        """Delete all execution event logs for all executions belonging to a campaign."""
        # Find all execution IDs for this campaign
        exec_stmt = select(Execution.id).where(Execution.campaign_id == campaign_id)
        result = await self.db.execute(
            delete(ExecutionEvent).where(ExecutionEvent.execution_id.in_(exec_stmt))
        )
        await self.db.flush()
        return result.rowcount

    async def delete_execution(self, execution_id: uuid.UUID) -> bool:
        """Delete an execution and completely clear its data (events, runs, compliance, assets)."""
        execution = await self.get_execution(execution_id)
        if not execution:
            return False

        campaign_id = execution.campaign_id

        # 1. Delete generated assets tied to this execution or for this campaign
        await self.db.execute(
            delete(GeneratedAsset).where(
                (GeneratedAsset.execution_id == execution_id) |
                (GeneratedAsset.campaign_id == campaign_id)
            )
        )

        # 2. Delete execution (cascades to events, agent_runs, guardrail_results, violations)
        await self.db.delete(execution)
        await self.db.flush()

        # 3. If no executions remain for this campaign, reset its status to DRAFT
        rem_res = await self.db.execute(
            select(Execution).where(Execution.campaign_id == campaign_id)
        )
        remaining = list(rem_res.scalars().all())
        if not remaining:
            camp_res = await self.db.execute(
                select(Campaign).where(Campaign.id == campaign_id)
            )
            campaign = camp_res.scalar_one_or_none()
            if campaign:
                campaign.status = CampaignStatus.DRAFT
                await self.db.flush()

        return True

    async def delete_campaign_executions(self, campaign_id: uuid.UUID) -> int:
        """Delete all executions, logs, and assets for a campaign, resetting it to draft."""
        # 1. Delete all assets for this campaign
        await self.db.execute(
            delete(GeneratedAsset).where(GeneratedAsset.campaign_id == campaign_id)
        )

        # 2. Delete all executions for this campaign (cascades to events, runs, compliance)
        exec_res = await self.db.execute(
            delete(Execution).where(Execution.campaign_id == campaign_id)
        )
        deleted_count = exec_res.rowcount

        # 3. Reset campaign status to draft
        camp_res = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        campaign = camp_res.scalar_one_or_none()
        if campaign:
            campaign.status = CampaignStatus.DRAFT

        await self.db.flush()
        return deleted_count



