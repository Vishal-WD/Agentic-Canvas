"""O&G Agentic Canvas - Agent Unit Tests."""

import asyncio
import pytest
from app.agents.base import AgentInput
from app.agents.copywriter import CopywriterAgent
from app.agents.layout import LayoutAgent
from app.agents.asset_recommender import AssetRecommenderAgent


@pytest.mark.asyncio
async def test_copywriter_mock_execution():
    agent = CopywriterAgent()
    input_data = AgentInput(
        campaign_brief="Autonomous agent orchestration platform with deep brand compliance and enterprise security.",
        campaign_type="social_media",
        target_audience="Security Architects & Engineering Leaders",
        brand_rules=[
            {"rule_id": "TONE-001", "content": "Maintain confident, authoritative enterprise tone."},
            {"rule_id": "COLOR-001", "content": "Use Deep Navy (#0C2140) and Guardrail Gold (#D6B25A)."},
        ],
    )
    result = await agent.safe_execute(input_data)
    assert result.success is True
    assert result.output is not None
    assert "headline" in result.output or "content" in result.output or "body" in result.output


@pytest.mark.asyncio
async def test_layout_mock_execution():
    agent = LayoutAgent()
    input_data = AgentInput(
        campaign_brief="Cloud security overview banner",
        campaign_type="landing_page",
        target_audience="IT Directors",
        brand_rules=[],
    )
    result = await agent.safe_execute(input_data)
    assert result.success is True
    assert result.output is not None


@pytest.mark.asyncio
async def test_asset_recommender_mock_execution():
    agent = AssetRecommenderAgent()
    input_data = AgentInput(
        campaign_brief="Enterprise infrastructure campaign",
        campaign_type="website",
        target_audience="DevSecOps",
        brand_rules=[],
    )
    result = await agent.safe_execute(input_data)
    assert result.success is True
    assert result.output is not None


@pytest.mark.asyncio
async def test_gemini_provider_503_fallback(monkeypatch):
    """Test that GoogleGeminiProvider handles 503 high-demand errors and activates fallback."""
    from app.agents.llm_provider import GoogleGeminiProvider
    from app.config import get_settings
    import httpx

    # Set fake google api key
    monkeypatch.setattr(get_settings(), "google_api_key", "fake-test-key")
    monkeypatch.setattr(get_settings(), "app_env", "development")

    provider = GoogleGeminiProvider()

    # Simulate 503 response from httpx
    call_counts = {"count": 0}
    def mock_handler(request: httpx.Request):
        call_counts["count"] += 1
        return httpx.Response(503, json={"error": {"code": 503, "message": "High demand", "status": "UNAVAILABLE"}})

    transport = httpx.MockTransport(mock_handler)
    _orig_client = httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda *args, **kwargs: _orig_client(transport=transport))

    async def noop_sleep(*args, **kwargs):
        pass

    monkeypatch.setattr("asyncio.sleep", noop_sleep)

    # Should gracefully activate continuity fallback without raising RuntimeError
    response = await provider.generate(
        system_prompt="You are Layout Agent",
        user_prompt="Create layout",
        response_format={"type": "json_object"}
    )
    assert response is not None
    assert response.provider == "gemini-continuity-fallback"
    assert response.content is not None
    assert call_counts["count"] > 1  # Verified that retries took place!

