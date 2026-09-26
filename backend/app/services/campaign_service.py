"""O&G Agentic Canvas - Campaign Service Layer."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Campaign, CampaignStatus, CampaignType, Execution, ExecutionStatus, GuardrailResult
from app.logging_config import get_logger
from app.schemas.models import CampaignCreate, DashboardSummary, ExecutionResponse

logger = get_logger("campaign_service")


class CampaignService:
    """Service layer for campaign operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_campaign(self, data: CampaignCreate) -> Campaign:
        """Create a new campaign."""
        campaign = Campaign(
            name=data.name,
            brief=data.brief,
            campaign_type=CampaignType(data.campaign_type.value),
            target_audience=data.target_audience,
            status=CampaignStatus.DRAFT,
        )
        self.db.add(campaign)
        await self.db.flush()
        await self.db.refresh(campaign)
        logger.info("campaign_created", campaign_id=str(campaign.id), name=campaign.name)
        return campaign

    async def get_campaign(self, campaign_id: uuid.UUID) -> Optional[Campaign]:
        """Get a campaign by ID."""
        result = await self.db.execute(
            select(Campaign).where(Campaign.id == campaign_id)
        )
        return result.scalar_one_or_none()

    async def list_campaigns(self, limit: int = 50, offset: int = 0) -> tuple[list[Campaign], int]:
        """List campaigns with pagination."""
        # Count
        count_result = await self.db.execute(select(func.count(Campaign.id)))
        total = count_result.scalar_one()

        # Fetch
        result = await self.db.execute(
            select(Campaign)
            .order_by(Campaign.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        campaigns = list(result.scalars().all())
        return campaigns, total

    async def update_campaign_status(self, campaign_id: uuid.UUID, status: CampaignStatus) -> Optional[Campaign]:
        """Update campaign status."""
        campaign = await self.get_campaign(campaign_id)
        if campaign:
            campaign.status = status
            await self.db.flush()
            await self.db.refresh(campaign)
            logger.info("campaign_status_updated", campaign_id=str(campaign_id), status=status.value)
        return campaign

    async def get_dashboard_summary(self) -> DashboardSummary:
        """Get dashboard summary metrics."""
        # Total campaigns
        total_result = await self.db.execute(select(func.count(Campaign.id)))
        total_campaigns = total_result.scalar_one()

        # Running executions
        running_result = await self.db.execute(
            select(func.count(Execution.id)).where(
                Execution.status.in_([
                    ExecutionStatus.RUNNING,
                    ExecutionStatus.GENERATING_COPY,
                    ExecutionStatus.STRUCTURING_LAYOUT,
                    ExecutionStatus.RECOMMENDING_ASSETS,
                    ExecutionStatus.VALIDATING_BRAND,
                    ExecutionStatus.REPAIRING,
                ])
            )
        )
        running_executions = running_result.scalar_one()

        # Approved / Completed
        approved_result = await self.db.execute(
            select(func.count(Execution.id)).where(
                Execution.status.in_([ExecutionStatus.APPROVED, ExecutionStatus.COMPLETED])
            )
        )
        approved_campaigns = approved_result.scalar_one()

        # Failed
        failed_result = await self.db.execute(
            select(func.count(Execution.id)).where(Execution.status == ExecutionStatus.FAILED)
        )
        failed_campaigns = failed_result.scalar_one()

        # Review required
        review_result = await self.db.execute(
            select(func.count(Execution.id)).where(Execution.status == ExecutionStatus.REVIEW_REQUIRED)
        )
        review_required = review_result.scalar_one()

        # Average compliance score
        avg_result = await self.db.execute(
            select(func.avg(GuardrailResult.overall_score))
        )
        avg_score = avg_result.scalar_one()

        # Recent executions
        recent_result = await self.db.execute(
            select(Execution)
            .order_by(Execution.started_at.desc().nulls_last())
            .limit(10)
        )
        recent_executions = list(recent_result.scalars().all())

        return DashboardSummary(
            total_campaigns=total_campaigns,
            running_executions=running_executions,
            approved_campaigns=approved_campaigns,
            failed_campaigns=failed_campaigns,
            review_required_campaigns=review_required,
            average_compliance_score=round(avg_score, 1) if avg_score else None,
            recent_executions=[
                ExecutionResponse.model_validate(e) for e in recent_executions
            ],
        )
