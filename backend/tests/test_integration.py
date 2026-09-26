"""O&G Agentic Canvas - End-to-End Orchestration Integration Test."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.session import async_session_factory
from app.main import app
from app.orchestration.executor import OrchestratorExecutor
from app.schemas.models import CampaignCreate, CampaignTypeEnum
from app.services.campaign_service import CampaignService
from app.services.execution_service import ExecutionService


@pytest.mark.asyncio
async def test_full_campaign_orchestration_lifecycle():
    """Test full pipeline: Campaign creation -> Execution -> Agents -> Guardrails -> Assets."""
    async with async_session_factory() as session:
        campaign_service = CampaignService(session)
        execution_service = ExecutionService(session)

        # 1. Create a campaign
        campaign_in = CampaignCreate(
            name="Enterprise Zero-Trust 2026",
            brief="Comprehensive campaign launching O&G autonomous agent orchestration with enterprise security and guardrails.",
            campaign_type=CampaignTypeEnum.WEBSITE,
            target_audience="Chief Information Security Officers and Enterprise Architects",
        )
        campaign = await campaign_service.create_campaign(campaign_in)
        assert campaign.id is not None
        assert campaign.name == "Enterprise Zero-Trust 2026"

        # 2. Create an execution
        execution = await execution_service.create_execution(campaign.id)
        assert execution.id is not None
        assert execution.current_state == "created"

        # 3. Run the orchestration pipeline
        executor = OrchestratorExecutor(session)
        await executor.run(execution.id)

        # 4. Refresh execution state
        updated_exec = await execution_service.get_execution(execution.id)
        assert updated_exec is not None
        assert updated_exec.status.value in ("approved", "review_required", "completed")
        assert updated_exec.final_score is not None
        assert updated_exec.final_score > 0

        # 5. Verify agent runs were recorded
        agent_runs = await execution_service.get_agent_runs(execution.id)
        agent_names = [run.agent_name for run in agent_runs]
        assert "copywriter" in agent_names
        assert "layout_structurer" in agent_names
        assert "asset_recommender" in agent_names


        # 6. Verify generated assets exist
        assets = await execution_service.get_generated_assets(campaign.id)
        assert len(assets) > 0


        # 7. Verify execution trace events
        events = await execution_service.get_execution_events(execution.id)
        assert len(events) >= 3


@pytest.mark.asyncio
async def test_api_campaign_and_dashboard_flow():
    """Test REST API endpoints: list rules, list campaigns, dashboard metrics."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get brand rules
        rules_res = await client.get("/api/brand/rules")
        assert rules_res.status_code == 200
        rules = rules_res.json()
        assert len(rules) > 0

        # Get dashboard metrics
        dash_res = await client.get("/api/dashboard/summary")
        assert dash_res.status_code == 200
        dash_data = dash_res.json()
        assert "total_campaigns" in dash_data
        assert dash_data["total_campaigns"] >= 1
