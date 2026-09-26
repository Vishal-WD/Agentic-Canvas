"""O&G Agentic Canvas - Brand Rules API Routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BrandRule
from app.db.session import get_db
from app.schemas.models import BrandRuleResponse

router = APIRouter(prefix="/brand", tags=["Brand"])


@router.get("/rules", response_model=list[BrandRuleResponse])
async def get_brand_rules(
    category: str | None = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db),
):
    """Get all active brand rules, optionally filtered by category."""
    query = select(BrandRule).where(BrandRule.active == True)

    if category:
        query = query.where(BrandRule.category == category)

    query = query.order_by(BrandRule.category, BrandRule.rule_id)

    result = await db.execute(query)
    rules = list(result.scalars().all())
    return [BrandRuleResponse.model_validate(r) for r in rules]


@router.get("/palette")
async def get_brand_palette():
    """Get approved brand colors and gradient pairings."""
    from app.guardrails.deterministic import APPROVED_COLORS, APPROVED_GRADIENTS
    return {
        "palette": [{"hex": hex_code, "name": name} for hex_code, name in APPROVED_COLORS.items()],
        "gradients": [{"start": g[0], "end": g[1]} for g in APPROVED_GRADIENTS],
    }

