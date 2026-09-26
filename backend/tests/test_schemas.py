"""O&G Agentic Canvas - Schema Unit Tests."""

import uuid
import pytest
from pydantic import ValidationError

from app.schemas.models import (
    CampaignCreate,
    CampaignResponse,
    CampaignTypeEnum,
    CampaignStatusEnum,
    ExecutionCreate,
    ViolationResponse,
    ViolationSeverityEnum,
)


def test_campaign_create_valid():
    campaign = CampaignCreate(
        name="Q3 Zero-Trust Launch",
        brief="Launch campaign for the new enterprise zero-trust security suite.",
        campaign_type=CampaignTypeEnum.SOCIAL_MEDIA,
        target_audience="CISOs and VP Infrastructure",
    )
    assert campaign.name == "Q3 Zero-Trust Launch"
    assert campaign.campaign_type == CampaignTypeEnum.SOCIAL_MEDIA


def test_campaign_create_invalid_brief():
    with pytest.raises(ValidationError):
        CampaignCreate(
            name="Valid Name",
            brief="Short",  # Min length is 10
            campaign_type=CampaignTypeEnum.SOCIAL_MEDIA,
            target_audience="Enterprise leaders",
        )


def test_execution_create():
    exec_req = ExecutionCreate(idempotency_key="idemp-12345")
    assert exec_req.idempotency_key == "idemp-12345"


def test_violation_response():
    v = ViolationResponse(
        id=uuid.uuid4(),
        rule_id="COLOR-001",
        severity=ViolationSeverityEnum.CRITICAL,
        field="background_color",
        expected="Approved O&G palette",
        actual="#FF0000",
        message="Non-approved color #FF0000",
        suggested_fix="Use Deep Navy (#0C2140)",
    )
    assert v.rule_id == "COLOR-001"
    assert v.severity == ViolationSeverityEnum.CRITICAL
