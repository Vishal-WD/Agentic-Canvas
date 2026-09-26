"""O&G Agentic Canvas - Execution API Routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.models import (
    ComplianceResponse,
    ExecutionEventResponse,
    ExecutionResponse,
    ViolationResponse,
)
from app.services.execution_service import ExecutionService

router = APIRouter(prefix="/executions", tags=["Executions"])


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get execution details."""
    service = ExecutionService(db)
    execution = await service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return ExecutionResponse.model_validate(execution)


@router.get("/{execution_id}/events", response_model=list[ExecutionEventResponse])
async def get_execution_events(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get execution events ordered by sequence."""
    service = ExecutionService(db)

    # Verify execution exists
    execution = await service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    events = await service.get_execution_events(execution_id)
    return [ExecutionEventResponse.model_validate(e) for e in events]


@router.get("/{execution_id}/compliance", response_model=list[ComplianceResponse])
async def get_compliance(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get compliance/guardrail results for an execution."""
    service = ExecutionService(db)

    execution = await service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    results = await service.get_compliance_results(execution_id)
    return [
        ComplianceResponse(
            id=r.id,
            execution_id=r.execution_id,
            overall_score=r.overall_score,
            category_scores=r.category_scores,
            status=r.status.value if hasattr(r.status, 'value') else r.status,
            critical_violation=r.critical_violation,
            evaluator_version=r.evaluator_version,
            attempt_number=r.attempt_number,
            violations=[ViolationResponse.model_validate(v) for v in (r.violations or [])],
            created_at=r.created_at,
        )
        for r in results
    ]


@router.delete("/{execution_id}/events")
async def clear_execution_events(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete all trace events / logs for a specific execution."""
    service = ExecutionService(db)
    execution = await service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    count = await service.delete_execution_events(execution_id)
    return {"status": "cleared", "deleted_count": count}


@router.delete("/{execution_id}")
async def delete_execution(
    execution_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Delete an execution and completely clear all its data (events, runs, compliance, assets)."""
    service = ExecutionService(db)
    execution = await service.get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    await service.delete_execution(execution_id)
    return {"status": "deleted", "id": str(execution_id)}


