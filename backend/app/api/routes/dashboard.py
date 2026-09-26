"""O&G Agentic Canvas - Dashboard API Routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.models import DashboardSummary
from app.services.campaign_service import CampaignService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard summary metrics."""
    service = CampaignService(db)
    return await service.get_dashboard_summary()
