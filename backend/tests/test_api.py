"""O&G Agentic Canvas - Comprehensive API Route Tests.

Verifies Section 35 API test cases against FastAPI endpoints.
"""

import uuid
import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_health_check():
    """GET /health -> 200 and valid health structure."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded", "ready")
        assert "version" in data


@pytest.mark.asyncio
async def test_brand_palette():
    """GET /brand/palette -> returns approved O&G colors."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/brand/palette")
        assert response.status_code == 200
        data = response.json()
        assert "palette" in data
        assert any(c["hex"] == "#0C2140" for c in data["palette"])
        assert any(c["hex"] == "#D6B25A" for c in data["palette"])


@pytest.mark.asyncio
async def test_campaign_create_valid():
    """POST /campaigns with valid input -> 201 + valid campaign schema."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "name": f"API Test Campaign {uuid.uuid4().hex[:6]}",
            "brief": "A launch campaign for enterprise zero-trust autonomous AI systems.",
            "campaign_type": "website",
            "target_audience": "Chief Information Security Officers and Enterprise Architects",
        }
        response = await client.post("/api/campaigns", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["campaign_type"] == "website"
        assert "id" in data


@pytest.mark.asyncio
async def test_campaign_create_empty_brief():
    """POST /campaigns with empty brief -> 422 validation error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "name": "Invalid Brief Campaign",
            "brief": "",  # Empty
            "campaign_type": "website",
            "target_audience": "Enterprise Architects",
        }
        response = await client.post("/api/campaigns", json=payload)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_campaign_create_invalid_type():
    """POST /campaigns with invalid campaign_type -> 422 validation error."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "name": "Invalid Type Campaign",
            "brief": "Valid brief describing the campaign goals in detail.",
            "campaign_type": "invalid_nonexistent_type",
            "target_audience": "Enterprise Architects",
        }
        response = await client.post("/api/campaigns", json=payload)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_campaign_executions_and_idempotency():
    """POST /campaigns/{id}/execute with idempotency key -> returns same execution on duplicate."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create a campaign
        camp_res = await client.post("/api/campaigns", json={
            "name": f"Idempotency Test {uuid.uuid4().hex[:6]}",
            "brief": "Brief for testing idempotency on campaign executions.",
            "campaign_type": "product_dashboard",
            "target_audience": "Product Engineers",
        })
        assert camp_res.status_code == 201
        camp_id = camp_res.json()["id"]

        # 2. Execute with unique idempotency key
        idem_key = f"key-{uuid.uuid4().hex}"
        exec_res1 = await client.post(f"/api/campaigns/{camp_id}/execute", json={
            "idempotency_key": idem_key
        })
        assert exec_res1.status_code == 201
        exec_id1 = exec_res1.json()["id"]

        # 3. Duplicate execution request with same idempotency key
        exec_res2 = await client.post(f"/api/campaigns/{camp_id}/execute", json={
            "idempotency_key": idem_key
        })
        assert exec_res2.status_code == 201
        exec_id2 = exec_res2.json()["id"]
        assert exec_id1 == exec_id2, "Idempotency key must return the existing execution ID"

        # 4. Check GET /campaigns/{id}/executions
        list_res = await client.get(f"/api/campaigns/{camp_id}/executions")
        assert list_res.status_code == 200
        executions = list_res.json()
        assert len(executions) >= 1
        assert any(e["id"] == exec_id1 for e in executions)


@pytest.mark.asyncio
async def test_webhook_alert_endpoint():
    """POST /api/webhook/alert -> 200 and processes alert safely."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "event": "n8n_orchestration_complete",
            "execution_id": str(uuid.uuid4()),
            "status": "approved",
            "score": 98.5,
            "details": {"source": "n8n_test"},
        }
        response = await client.post("/api/webhook/alert", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
        assert data["processed"] is True


@pytest.mark.asyncio
async def test_asset_crud_and_log_clearing():
    """Test modifying and deleting generated assets, as well as clearing logs."""
    from app.db.session import async_session_factory
    from app.db.models import GeneratedAsset, Execution, ExecutionEvent, ExecutionStatus

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create a campaign
        camp_res = await client.post("/api/campaigns", json={
            "name": f"Asset Test Campaign {uuid.uuid4().hex[:6]}",
            "brief": "Testing asset modification and log deletion.",
            "campaign_type": "website",
            "target_audience": "DevOps Engineers",
        })
        assert camp_res.status_code == 201
        camp_id = uuid.UUID(camp_res.json()["id"])

        # 2. Insert an asset and execution event directly into DB
        async with async_session_factory() as session:
            execution = Execution(
                campaign_id=camp_id,
                status=ExecutionStatus.RUNNING,
                current_state="generating_copy",
            )
            session.add(execution)
            await session.flush()

            asset = GeneratedAsset(
                campaign_id=camp_id,
                execution_id=execution.id,
                asset_type="copy",
                content={"headline": "Original Headline", "cta": "Click Here"},
                status="generated",
            )
            session.add(asset)

            event = ExecutionEvent(
                execution_id=execution.id,
                from_state="created",
                to_state="running",
                reason="Test start",
                sequence=1,
            )
            session.add(event)
            await session.commit()
            asset_id = asset.id
            exec_id = execution.id

        # 3. Test GET assets
        assets_res = await client.get(f"/api/campaigns/{camp_id}/assets")
        assert assets_res.status_code == 200
        assert len(assets_res.json()) >= 1

        # 4. Test PUT/modify asset
        update_res = await client.put(f"/api/campaigns/{camp_id}/assets/{asset_id}", json={
            "content": {"headline": "Modified Headline", "cta": "Schedule Demo Now"},
            "status": "approved",
        })
        assert update_res.status_code == 200
        updated_data = update_res.json()
        assert updated_data["content"]["headline"] == "Modified Headline"
        assert updated_data["status"] == "approved"

        # 5. Test DELETE execution events / logs
        clear_events_res = await client.delete(f"/api/executions/{exec_id}/events")
        assert clear_events_res.status_code == 200
        assert clear_events_res.json()["status"] == "cleared"

        # Verify events are now empty
        events_res = await client.get(f"/api/executions/{exec_id}/events")
        assert events_res.status_code == 200
        assert len(events_res.json()) == 0

        # 6. Test DELETE single asset
        delete_asset_res = await client.delete(f"/api/campaigns/{camp_id}/assets/{asset_id}")
        assert delete_asset_res.status_code == 200
        assert delete_asset_res.json()["status"] == "deleted"

        # Verify asset is gone
        assets_after = await client.get(f"/api/campaigns/{camp_id}/assets")
        assert len(assets_after.json()) == 0

        # 7. Test DELETE campaign logs endpoint
        camp_logs_del = await client.delete(f"/api/campaigns/{camp_id}/logs")
        assert camp_logs_del.status_code == 200
        assert camp_logs_del.json()["status"] == "cleared"

        # 8. Test DELETE execution endpoint (and complete data clearing)
        del_exec_res = await client.delete(f"/api/executions/{exec_id}")
        assert del_exec_res.status_code == 200
        assert del_exec_res.json()["status"] == "deleted"

        # Verify execution is 404
        get_exec_404 = await client.get(f"/api/executions/{exec_id}")
        assert get_exec_404.status_code == 404

        # 9. Test DELETE all executions for campaign
        del_camp_execs = await client.delete(f"/api/campaigns/{camp_id}/executions")
        assert del_camp_execs.status_code == 200
        assert del_camp_execs.json()["status"] == "deleted"


