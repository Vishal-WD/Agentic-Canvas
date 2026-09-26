"""O&G Agentic Canvas - Campaign API Routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db
from app.schemas.models import (
    CampaignCreate,
    CampaignListResponse,
    CampaignResponse,
    ExecutionCreate,
    ExecutionResponse,
    GeneratedAssetResponse,
    GeneratedAssetUpdateRequest,
)
from app.services.campaign_service import CampaignService
from app.services.execution_service import ExecutionService

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new campaign."""
    service = CampaignService(db)
    campaign = await service.create_campaign(data)
    return CampaignResponse.model_validate(campaign)


@router.get("", response_model=CampaignListResponse)
async def list_campaigns(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List all campaigns with pagination."""
    service = CampaignService(db)
    campaigns, total = await service.list_campaigns(limit=limit, offset=offset)
    return CampaignListResponse(
        campaigns=[CampaignResponse.model_validate(c) for c in campaigns],
        total=total,
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a campaign by ID."""
    service = CampaignService(db)
    campaign = await service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return CampaignResponse.model_validate(campaign)


@router.post(
    "/{campaign_id}/execute",
    response_model=ExecutionResponse,
    status_code=status.HTTP_201_CREATED,
)
@router.post(
    "/{campaign_id}/executions",
    response_model=ExecutionResponse,
    status_code=status.HTTP_201_CREATED,
)

async def start_execution(
    campaign_id: uuid.UUID,
    data: ExecutionCreate = ExecutionCreate(),
    db: AsyncSession = Depends(get_db),
):
    """Start a new execution for a campaign."""
    # Verify campaign exists
    campaign_service = CampaignService(db)
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    execution_service = ExecutionService(db)
    execution = await execution_service.create_execution(
        campaign_id=campaign_id,
        idempotency_key=data.idempotency_key,
    )

    # Trigger orchestration asynchronously with a dedicated database session
    settings = get_settings()
    print(f"DEBUG start_execution: app_env={settings.app_env}, is_testing={settings.is_testing}")
    if not settings.is_testing:
        import asyncio
        from app.db.session import async_session_factory
        from app.orchestration.executor import OrchestratorExecutor

        async def _run_in_background(exec_id: uuid.UUID):
            try:
                async with async_session_factory() as bg_session:
                    bg_executor = OrchestratorExecutor(bg_session)
                    await bg_executor.run(exec_id)
            except Exception as e:
                import traceback
                print(f"[ERROR in _run_in_background]: {e}\n{traceback.format_exc()}")

        task = asyncio.create_task(_run_in_background(execution.id))

    return ExecutionResponse.model_validate(execution)



@router.get("/{campaign_id}/executions", response_model=list[ExecutionResponse])
async def get_campaign_executions(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all executions for a campaign."""
    campaign_service = CampaignService(db)
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    execution_service = ExecutionService(db)
    executions = await execution_service.get_campaign_executions(campaign_id)
    return [ExecutionResponse.model_validate(e) for e in executions]


@router.get("/{campaign_id}/assets", response_model=list[GeneratedAssetResponse])
async def get_campaign_assets(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get generated assets for a campaign."""
    # Verify campaign exists
    campaign_service = CampaignService(db)
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    execution_service = ExecutionService(db)
    assets = await execution_service.get_generated_assets(campaign_id)
    return [GeneratedAssetResponse.model_validate(a) for a in assets]


@router.put("/{campaign_id}/assets/{asset_id}", response_model=GeneratedAssetResponse)
@router.patch("/{campaign_id}/assets/{asset_id}", response_model=GeneratedAssetResponse)
async def update_campaign_asset(
    campaign_id: uuid.UUID,
    asset_id: uuid.UUID,
    data: GeneratedAssetUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Modify/update a generated asset for a campaign."""
    campaign_service = CampaignService(db)
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    execution_service = ExecutionService(db)
    asset = await execution_service.get_generated_asset(asset_id)
    if not asset or asset.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Asset not found for this campaign")

    updated = await execution_service.update_generated_asset(
        asset_id=asset_id,
        content=data.content,
        status=data.status,
    )
    return GeneratedAssetResponse.model_validate(updated)


@router.delete("/{campaign_id}/assets/{asset_id}")
async def delete_campaign_asset(
    campaign_id: uuid.UUID,
    asset_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete a single generated asset."""
    campaign_service = CampaignService(db)
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    execution_service = ExecutionService(db)
    asset = await execution_service.get_generated_asset(asset_id)
    if not asset or asset.campaign_id != campaign_id:
        raise HTTPException(status_code=404, detail="Asset not found for this campaign")

    await execution_service.delete_generated_asset(asset_id)
    return {"status": "deleted", "id": str(asset_id)}


@router.delete("/{campaign_id}/assets")
async def delete_all_campaign_assets(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete all generated assets for a campaign."""
    campaign_service = CampaignService(db)
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    execution_service = ExecutionService(db)
    count = await execution_service.delete_campaign_assets(campaign_id)
    return {"status": "deleted", "deleted_count": count}


@router.delete("/{campaign_id}/logs")
async def clear_campaign_logs(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete all previous execution event trace logs for a campaign."""
    campaign_service = CampaignService(db)
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    execution_service = ExecutionService(db)
    count = await execution_service.delete_campaign_logs(campaign_id)
    return {"status": "cleared", "deleted_count": count}


@router.delete("/{campaign_id}/executions")
async def delete_campaign_executions(
    campaign_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete all executions, logs, and generated assets for a campaign, resetting it to draft."""
    campaign_service = CampaignService(db)
    campaign = await campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    execution_service = ExecutionService(db)
    count = await execution_service.delete_campaign_executions(campaign_id)
    return {"status": "deleted", "deleted_count": count}



