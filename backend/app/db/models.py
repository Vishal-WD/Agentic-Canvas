"""O&G Agentic Canvas - SQLAlchemy Database Models.

All models use UUID primary keys, timestamps, and proper foreign key relationships.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import JSON, Uuid as UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_uuid() -> uuid.UUID:
    return uuid.uuid4()


# ─── Enums ────────────────────────────────────────────────────────────

class CampaignStatus(str, PyEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"


class CampaignType(str, PyEnum):
    WEBSITE = "website"
    LANDING_PAGE = "landing_page"
    PITCH_DECK = "pitch_deck"
    PRODUCT_DASHBOARD = "product_dashboard"
    DEVELOPER_ASSETS = "developer_assets"
    SOCIAL_MEDIA = "social_media"
    REPORT = "report"


class ExecutionStatus(str, PyEnum):
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


class AgentRunStatus(str, PyEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class GuardrailStatus(str, PyEnum):
    PASSED = "passed"
    FAILED = "failed"
    REVIEW_REQUIRED = "review_required"


class ViolationSeverity(str, PyEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class UserRole(str, PyEnum):
    ADMIN = "admin"
    BRAND_GUARDIAN = "brand_guardian"
    CAMPAIGN_ARCHITECT = "campaign_architect"
    COMPLIANCE_OFFICER = "compliance_officer"


# ─── Models ────────────────────────────────────────────────────────────

class User(Base):
    """User account for enterprise access."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRole, name="user_role_enum", native_enum=False),
        nullable=False,
        default=UserRole.CAMPAIGN_ARCHITECT,
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    def __repr__(self) -> str:
        return f"<User {self.email} ({self.role})>"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    name = Column(String(255), nullable=False)
    brief = Column(Text, nullable=False)
    campaign_type = Column(
        Enum(CampaignType, name="campaign_type_enum", create_constraint=True),
        nullable=False,
    )
    target_audience = Column(Text, nullable=False)
    status = Column(
        Enum(CampaignStatus, name="campaign_status_enum", create_constraint=True),
        nullable=False,
        default=CampaignStatus.DRAFT,
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    creator = relationship("User", backref="campaigns", lazy="selectin")
    executions = relationship("Execution", back_populates="campaign", lazy="selectin")
    generated_assets = relationship("GeneratedAsset", back_populates="campaign", lazy="selectin")

    __table_args__ = (
        Index("ix_campaigns_status", "status"),
        Index("ix_campaigns_created_at", "created_at"),
        Index("ix_campaigns_creator_id", "creator_id"),
    )


class Execution(Base):
    __tablename__ = "executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    status = Column(
        Enum(ExecutionStatus, name="execution_status_enum", create_constraint=True),
        nullable=False,
        default=ExecutionStatus.CREATED,
    )
    current_state = Column(String(50), nullable=False, default="created")
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    final_score = Column(Float, nullable=True)
    failure_reason = Column(Text, nullable=True)
    idempotency_key = Column(String(255), nullable=True)

    # Relationships
    campaign = relationship("Campaign", back_populates="executions")
    events = relationship("ExecutionEvent", back_populates="execution", lazy="selectin", order_by="ExecutionEvent.sequence")
    agent_runs = relationship("AgentRun", back_populates="execution", lazy="selectin")
    guardrail_results = relationship("GuardrailResult", back_populates="execution", lazy="selectin")
    generated_assets = relationship("GeneratedAsset", back_populates="execution", lazy="selectin")

    __table_args__ = (
        Index("ix_executions_campaign_id", "campaign_id"),
        Index("ix_executions_status", "status"),
        UniqueConstraint("idempotency_key", name="uq_executions_idempotency_key"),
    )


class ExecutionEvent(Base):
    __tablename__ = "execution_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False)
    from_state = Column(String(50), nullable=True)
    to_state = Column(String(50), nullable=False)
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    sequence = Column(Integer, nullable=False)

    # Relationships
    execution = relationship("Execution", back_populates="events")

    __table_args__ = (
        Index("ix_execution_events_execution_id", "execution_id"),
        Index("ix_execution_events_sequence", "execution_id", "sequence"),
    )


class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    agent_version = Column(String(20), nullable=False, default="1.0")
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    status = Column(
        Enum(AgentRunStatus, name="agent_run_status_enum", create_constraint=True),
        nullable=False,
        default=AgentRunStatus.PENDING,
    )
    model_provider = Column(String(50), nullable=True)
    latency_ms = Column(Float, nullable=True)
    token_usage = Column(JSON, nullable=True)
    attempt_number = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    execution = relationship("Execution", back_populates="agent_runs")

    __table_args__ = (
        Index("ix_agent_runs_execution_id", "execution_id"),
        Index("ix_agent_runs_agent_name", "agent_name"),
    )


class GeneratedAsset(Base):
    __tablename__ = "generated_assets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("executions.id", ondelete="SET NULL"), nullable=True)
    asset_type = Column(String(50), nullable=False)
    content = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, default="generated")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="generated_assets")
    execution = relationship("Execution", back_populates="generated_assets")

    __table_args__ = (
        Index("ix_generated_assets_campaign_id", "campaign_id"),
    )


class BrandRule(Base):
    __tablename__ = "brand_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    rule_id = Column(String(50), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False, default="1.0")
    priority = Column(String(20), nullable=False, default="medium")
    source = Column(String(100), nullable=False, default="O&G Brand Kit")
    content = Column(Text, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    __table_args__ = (
        Index("ix_brand_rules_category", "category"),
        Index("ix_brand_rules_rule_id", "rule_id"),
    )


class GuardrailResult(Base):
    __tablename__ = "guardrail_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    execution_id = Column(UUID(as_uuid=True), ForeignKey("executions.id", ondelete="CASCADE"), nullable=False)
    overall_score = Column(Float, nullable=False)
    category_scores = Column(JSON, nullable=True)
    status = Column(
        Enum(GuardrailStatus, name="guardrail_status_enum", create_constraint=True),
        nullable=False,
    )
    critical_violation = Column(Boolean, nullable=False, default=False)
    evaluator_version = Column(String(20), nullable=False, default="1.0")
    attempt_number = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    # Relationships
    execution = relationship("Execution", back_populates="guardrail_results")
    violations = relationship("GuardrailViolation", back_populates="guardrail_result", lazy="selectin")

    __table_args__ = (
        Index("ix_guardrail_results_execution_id", "execution_id"),
    )


class GuardrailViolation(Base):
    __tablename__ = "guardrail_violations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=new_uuid)
    guardrail_result_id = Column(UUID(as_uuid=True), ForeignKey("guardrail_results.id", ondelete="CASCADE"), nullable=False)
    rule_id = Column(String(50), nullable=False)
    severity = Column(
        Enum(ViolationSeverity, name="violation_severity_enum", create_constraint=True),
        nullable=False,
    )
    field = Column(String(100), nullable=True)
    expected = Column(Text, nullable=True)
    actual = Column(Text, nullable=True)
    message = Column(Text, nullable=False)
    suggested_fix = Column(Text, nullable=True)

    # Relationships
    guardrail_result = relationship("GuardrailResult", back_populates="violations")

    __table_args__ = (
        Index("ix_guardrail_violations_result_id", "guardrail_result_id"),
        Index("ix_guardrail_violations_severity", "severity"),
    )
