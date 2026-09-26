"""O&G Agentic Canvas - Pydantic Schemas for API Request/Response Models."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ─── Enums ────────────────────────────────────────────────────────────

class CampaignTypeEnum(str, Enum):
    WEBSITE = "website"
    LANDING_PAGE = "landing_page"
    PITCH_DECK = "pitch_deck"
    PRODUCT_DASHBOARD = "product_dashboard"
    DEVELOPER_ASSETS = "developer_assets"
    SOCIAL_MEDIA = "social_media"
    REPORT = "report"


class CampaignStatusEnum(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionStatusEnum(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    GENERATING_COPY = "generating_copy"
    STRUCTURING_LAYOUT = "structuring_layout"
    RECOMMENDING_ASSETS = "recommending_assets"
    VALIDATING_BRAND = "validating_brand"
    REPAIRING = "repairing"
    APPROVED = "approved"
    REVIEW_REQUIRED = "review_required"
    FAILED = "failed"
    COMPLETED = "completed"


class ViolationSeverityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


# ─── Campaign Schemas ────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    """Request schema for creating a campaign."""
    name: str = Field(..., min_length=1, max_length=255, description="Campaign name")
    brief: str = Field(..., min_length=10, max_length=5000, description="Campaign brief/description")
    campaign_type: CampaignTypeEnum = Field(..., description="Type of campaign")
    target_audience: str = Field(..., min_length=5, max_length=2000, description="Target audience description")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Campaign name cannot be blank")
        return v.strip()

    @field_validator("brief")
    @classmethod
    def brief_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Campaign brief cannot be blank")
        return v.strip()


class CampaignResponse(BaseModel):
    """Response schema for a campaign."""
    id: uuid.UUID
    name: str
    brief: str
    campaign_type: CampaignTypeEnum
    target_audience: str
    status: CampaignStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CampaignListResponse(BaseModel):
    """Response schema for campaign list."""
    campaigns: list[CampaignResponse]
    total: int


# ─── Execution Schemas ───────────────────────────────────────────────

class ExecutionCreate(BaseModel):
    """Request schema for starting an execution."""
    idempotency_key: Optional[str] = Field(None, max_length=255, description="Idempotency key to prevent duplicate executions")


class ExecutionResponse(BaseModel):
    """Response schema for an execution."""
    id: uuid.UUID
    campaign_id: uuid.UUID
    status: ExecutionStatusEnum
    current_state: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    final_score: Optional[float] = None
    failure_reason: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Execution Event Schemas ─────────────────────────────────────────

class ExecutionEventResponse(BaseModel):
    """Response schema for an execution event."""
    id: uuid.UUID
    execution_id: uuid.UUID
    from_state: Optional[str] = None
    to_state: str
    reason: Optional[str] = None
    timestamp: datetime
    sequence: int

    model_config = {"from_attributes": True}


# ─── Agent Run Schemas ───────────────────────────────────────────────

class AgentRunResponse(BaseModel):
    """Response schema for an agent run."""
    id: uuid.UUID
    execution_id: uuid.UUID
    agent_name: str
    agent_version: str
    status: str
    model_provider: Optional[str] = None
    latency_ms: Optional[float] = None
    attempt_number: int
    output_data: Optional[dict[str, Any]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Guardrail Schemas ───────────────────────────────────────────────

class ViolationResponse(BaseModel):
    """Response schema for a guardrail violation."""
    id: uuid.UUID
    rule_id: str
    severity: ViolationSeverityEnum
    field: Optional[str] = None
    expected: Optional[str] = None
    actual: Optional[str] = None
    message: str
    suggested_fix: Optional[str] = None

    model_config = {"from_attributes": True}


class ComplianceResponse(BaseModel):
    """Response schema for compliance/guardrail results."""
    id: uuid.UUID
    execution_id: uuid.UUID
    overall_score: float
    category_scores: Optional[dict[str, float]] = None
    status: str
    critical_violation: bool
    evaluator_version: str
    attempt_number: int
    violations: list[ViolationResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Brand Rule Schemas ──────────────────────────────────────────────

class BrandRuleResponse(BaseModel):
    """Response schema for a brand rule."""
    id: uuid.UUID
    rule_id: str
    category: str
    version: str
    priority: str
    source: str
    content: str
    active: bool

    model_config = {"from_attributes": True}


# ─── Dashboard Schemas ───────────────────────────────────────────────

class DashboardSummary(BaseModel):
    """Response schema for dashboard summary metrics."""
    total_campaigns: int = 0
    running_executions: int = 0
    approved_campaigns: int = 0
    failed_campaigns: int = 0
    review_required_campaigns: int = 0
    average_compliance_score: Optional[float] = None
    recent_executions: list[ExecutionResponse] = []


# ─── Generated Asset Schemas ─────────────────────────────────────────

class GeneratedAssetResponse(BaseModel):
    """Response schema for a generated asset."""
    id: uuid.UUID
    campaign_id: uuid.UUID
    execution_id: Optional[uuid.UUID] = None
    asset_type: str
    content: dict[str, Any]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class GeneratedAssetUpdateRequest(BaseModel):
    """Request schema for updating or modifying a generated asset."""
    content: Optional[dict[str, Any]] = None
    status: Optional[str] = None


# ─── Health Schema ───────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str
    environment: str
    database: str = "unknown"
    timestamp: datetime


# ─── Agent Output Schemas (for LLM validation) ──────────────────────

class CopywriterOutput(BaseModel):
    """Schema for Copywriter Agent output."""
    headline: str = Field(..., min_length=1, description="Campaign headline")
    subheadline: str = Field(default="", description="Campaign subheadline")
    value_proposition: str = Field(default="", description="Value proposition")
    cta: str = Field(default="", description="Call to action text")
    social_posts: list[str] = Field(default_factory=list, description="Social media copy")
    supporting_copy: str = Field(default="", description="Supporting body copy")
    brand_context_used: list[dict[str, str]] = Field(default_factory=list, description="Brand rules referenced")

    @field_validator("subheadline", "value_proposition", "cta", "supporting_copy", mode="before")
    @classmethod
    def coerce_str(cls, v):
        return "" if v is None else str(v)


class LayoutSection(BaseModel):
    """Schema for a layout section."""
    section_id: str = Field(default="section-1")
    section_type: str = Field(default="content", description="e.g., hero, features, cta, testimonials, footer")
    content_key: str = Field(default="", description="Key mapping to copy content")
    background_color: Optional[str] = Field(default="#0C2140")
    text_color: Optional[str] = Field(default="#F5F8FC")
    accent_color: Optional[str] = None
    hierarchy_level: int = Field(default=1, ge=1, le=5)
    components: list[str] = Field(default_factory=list)
    placement: str = Field(default="full-width")

    @field_validator("background_color", mode="before")
    @classmethod
    def default_bg(cls, v):
        return v or "#0C2140"

    @field_validator("text_color", mode="before")
    @classmethod
    def default_text(cls, v):
        return v or "#F5F8FC"

    @field_validator("content_key", mode="before")
    @classmethod
    def default_content_key(cls, v):
        return "" if v is None else str(v)


class LayoutOutput(BaseModel):
    """Schema for Layout Structurer Agent output."""
    layout_type: str = Field(default="responsive_grid", description="Overall layout type")
    campaign_type: str = Field(default="website")
    sections: list[LayoutSection] = Field(..., min_length=1)
    visual_hierarchy: str = Field(default="standard")
    logo_placement: str = Field(default="top-left")
    logo_required: bool = Field(default=True)
    brand_context_used: list[dict[str, str]] = Field(default_factory=list)


class AssetRecommendation(BaseModel):
    """Schema for a single asset recommendation."""
    asset_type: str = Field(default="image", description="e.g., hero_image, icon, background, illustration")
    subject: str = Field(default="", description="Visual subject description")
    aspect_ratio: Optional[str] = Field(default="16:9")
    background_color: Optional[str] = Field(default="#0C2140")
    gradient: Optional[str] = None
    alt_text: str = Field(default="", description="Accessibility alt text")
    brand_restrictions: list[str] = Field(default_factory=list)

    @field_validator("background_color", mode="before")
    @classmethod
    def default_asset_bg(cls, v):
        return v or "#0C2140"

    @field_validator("aspect_ratio", mode="before")
    @classmethod
    def default_aspect(cls, v):
        return v or "16:9"

    @field_validator("alt_text", "subject", mode="before")
    @classmethod
    def default_str(cls, v):
        return "" if v is None else str(v)


class AssetRecommenderOutput(BaseModel):
    """Schema for Asset Recommender Agent output."""
    recommendations: list[AssetRecommendation] = Field(..., min_length=1)
    campaign_type: str = Field(default="website")
    brand_context_used: list[dict[str, str]] = Field(default_factory=list)


class SemanticEvaluationOutput(BaseModel):
    """Schema for Semantic Evaluator output."""
    semantic_score: float = Field(..., ge=0, le=100)
    violations: list[dict[str, Any]] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    status: str = Field(..., description="pass, fail, or review_required")
    evaluator_version: str = Field(default="1.0")
