"""O&G Agentic Canvas - Orchestration Executor.

Runs the complete agent pipeline: Copywriter → Layout → Assets → Guardrails → Repair.
Manages state transitions, event logging, and audit trail persistence.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings

from app.agents.asset_recommender import AssetRecommenderAgent
from app.agents.base import AgentInput, AgentResult
from app.agents.copywriter import CopywriterAgent
from app.agents.layout import LayoutAgent
from app.db.models import (
    AgentRun,
    AgentRunStatus,
    CampaignStatus,
    ExecutionStatus,
    GeneratedAsset,
    GuardrailResult as GuardrailResultModel,
    GuardrailStatus,
    GuardrailViolation as GuardrailViolationModel,
    ViolationSeverity,
)
from app.guardrails.engine import GuardrailEngine
from app.logging_config import get_logger
from app.rag.retrieval import BrandRAGService
from app.services.campaign_service import CampaignService
from app.services.execution_service import ExecutionService
from app.services.webhook_service import WebhookAlertService

logger = get_logger("orchestrator")


class OrchestratorExecutor:
    """Orchestrates the complete campaign execution pipeline with task dependency checks and webhook alerts."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.execution_service = ExecutionService(db)
        self.campaign_service = CampaignService(db)
        self.rag_service = BrandRAGService()
        self.guardrail_engine = GuardrailEngine()
        self.webhook_service = WebhookAlertService()


    async def run(self, execution_id: uuid.UUID) -> None:
        """Run the full orchestration pipeline for an execution."""
        try:
            execution = await self.execution_service.get_execution(execution_id)
            if not execution:
                logger.error("execution_not_found", execution_id=str(execution_id))
                return

            campaign = await self.campaign_service.get_campaign(execution.campaign_id)
            if not campaign:
                logger.error("campaign_not_found", campaign_id=str(execution.campaign_id))
                return

            logger.info(
                "orchestration_started",
                execution_id=str(execution_id),
                campaign_id=str(campaign.id),
                campaign_name=campaign.name,
            )

            # Update to RUNNING
            await self.execution_service.update_execution_state(
                execution_id, ExecutionStatus.RUNNING, "Orchestration started"
            )

            # Automated webhook alert: started
            await self.webhook_service.send_alert(
                event_type="execution_started",
                execution_id=execution_id,
                campaign_id=campaign.id,
                campaign_name=campaign.name,
                status="running",
            )

            # Ingest brand rules
            self.rag_service.ingest_brand_rules()


            # ─── Step 1: Copywriter ──────────────────────────────
            await self.execution_service.update_execution_state(
                execution_id, ExecutionStatus.GENERATING_COPY, "Running Copywriter Agent"
            )

            copy_rules = self.rag_service.retrieve_for_agent("copywriter", campaign.campaign_type.value)
            copy_input = AgentInput(
                campaign_brief=campaign.brief,
                campaign_type=campaign.campaign_type.value,
                target_audience=campaign.target_audience,
                brand_rules=copy_rules,
            )

            copywriter = CopywriterAgent()
            copy_result = await self._execute_agent_with_retry(copywriter, copy_input, execution_id)

            if not copy_result.success:
                await self._fail_execution(execution_id, f"Copywriter failed: {copy_result.error}")
                return

            # ─── Step 2: Layout Structurer ────────────────────────
            await self.execution_service.update_execution_state(
                execution_id, ExecutionStatus.STRUCTURING_LAYOUT, "Running Layout Structurer Agent"
            )

            layout_rules = self.rag_service.retrieve_for_agent("layout_structurer", campaign.campaign_type.value)
            layout_input = AgentInput(
                campaign_brief=campaign.brief,
                campaign_type=campaign.campaign_type.value,
                target_audience=campaign.target_audience,
                brand_rules=layout_rules,
                additional_context={"copy": copy_result.output},
            )

            layout_agent = LayoutAgent()
            layout_result = await self._execute_agent_with_retry(layout_agent, layout_input, execution_id)

            if not layout_result.success:
                await self._fail_execution(execution_id, f"Layout agent failed: {layout_result.error}")
                return

            # ─── Step 3: Asset Recommender ────────────────────────
            await self.execution_service.update_execution_state(
                execution_id, ExecutionStatus.RECOMMENDING_ASSETS, "Running Asset Recommender Agent"
            )

            asset_rules = self.rag_service.retrieve_for_agent("asset_recommender", campaign.campaign_type.value)
            asset_input = AgentInput(
                campaign_brief=campaign.brief,
                campaign_type=campaign.campaign_type.value,
                target_audience=campaign.target_audience,
                brand_rules=asset_rules,
                additional_context={"copy": copy_result.output, "layout": layout_result.output},
            )

            asset_agent = AssetRecommenderAgent()
            asset_result = await self._execute_agent_with_retry(asset_agent, asset_input, execution_id)

            if not asset_result.success:
                await self._fail_execution(execution_id, f"Asset recommender failed: {asset_result.error}")
                return

            # ─── Step 4: Brand Guardrails ─────────────────────────
            await self.execution_service.update_execution_state(
                execution_id, ExecutionStatus.VALIDATING_BRAND, "Running Brand Guardrails"
            )

            # Combine all outputs for validation
            combined_output = {
                **(copy_result.output or {}),
                **(layout_result.output or {}),
                **(asset_result.output or {}),
            }

            all_rules = self.rag_service.retrieve("brand guidelines color tone layout", top_k=20)

            # Run guardrails with repair loop
            final_output, compliance_score, repair_attempts = await self.guardrail_engine.validate_and_repair(
                campaign_output=combined_output,
                brand_rules=all_rules,
            )

            # Log repair attempts
            if len(repair_attempts) > 1:
                await self.execution_service.update_execution_state(
                    execution_id, ExecutionStatus.REPAIRING,
                    f"Repair attempted {len(repair_attempts) - 1} time(s)"
                )

            # ─── Step 5: Save Results ─────────────────────────────
            # Save guardrail result
            guardrail_status = GuardrailStatus.PASSED
            if compliance_score.status == "rejected":
                guardrail_status = GuardrailStatus.FAILED
            elif compliance_score.status == "review_required":
                guardrail_status = GuardrailStatus.REVIEW_REQUIRED

            guardrail_result = GuardrailResultModel(
                execution_id=execution_id,
                overall_score=compliance_score.overall_score,
                category_scores=compliance_score.category_scores,
                status=guardrail_status,
                critical_violation=compliance_score.has_critical_violation,
                evaluator_version="1.0",
                attempt_number=len(repair_attempts),
            )
            self.db.add(guardrail_result)
            await self.db.flush()

            # Save violations
            for violation in compliance_score.violations:
                severity_map = {
                    "critical": ViolationSeverity.CRITICAL,
                    "high": ViolationSeverity.HIGH,
                    "medium": ViolationSeverity.MEDIUM,
                    "low": ViolationSeverity.LOW,
                    "info": ViolationSeverity.INFO,
                }
                v = GuardrailViolationModel(
                    guardrail_result_id=guardrail_result.id,
                    rule_id=violation.get("rule_id", "UNKNOWN"),
                    severity=severity_map.get(violation.get("severity", "medium"), ViolationSeverity.MEDIUM),
                    field=violation.get("field", ""),
                    expected=violation.get("expected", ""),
                    actual=violation.get("actual", ""),
                    message=violation.get("message", ""),
                    suggested_fix=violation.get("suggested_fix", ""),
                )
                self.db.add(v)

            # Save generated assets
            for asset_type, content in [
                ("copy", copy_result.output),
                ("layout", layout_result.output),
                ("assets", asset_result.output),
            ]:
                if content:
                    asset = GeneratedAsset(
                        campaign_id=campaign.id,
                        execution_id=execution_id,
                        asset_type=asset_type,
                        content=content,
                        status="generated",
                    )
                    self.db.add(asset)

            # ─── Step 6: Final Status ─────────────────────────────
            if compliance_score.status == "passed":
                final_status = ExecutionStatus.APPROVED
                await self.campaign_service.update_campaign_status(campaign.id, CampaignStatus.COMPLETED)
            elif compliance_score.status == "review_required":
                final_status = ExecutionStatus.REVIEW_REQUIRED
            else:
                final_status = ExecutionStatus.FAILED

            await self.execution_service.update_execution_state(
                execution_id,
                final_status,
                f"Final compliance score: {compliance_score.overall_score:.1f} — {compliance_score.status}",
                final_score=compliance_score.overall_score,
                failure_reason=f"Violations: {len(compliance_score.violations)}" if compliance_score.violations else None,
            )

            # Update to COMPLETED
            if final_status == ExecutionStatus.APPROVED:
                await self.execution_service.update_execution_state(
                    execution_id, ExecutionStatus.COMPLETED, "Execution completed successfully"
                )

            await self.db.commit()

            # Automated webhook alert: completed
            await self.webhook_service.send_alert(
                event_type="execution_completed",
                execution_id=execution_id,
                campaign_id=campaign.id,
                campaign_name=campaign.name,
                status=final_status.value,
                score=compliance_score.overall_score,
                details={
                    "violations_count": len(compliance_score.violations),
                    "repair_attempts": len(repair_attempts),
                },
            )

            logger.info(
                "orchestration_completed",
                execution_id=str(execution_id),
                final_status=final_status.value,
                score=compliance_score.overall_score,
                violations=len(compliance_score.violations),
                repair_attempts=len(repair_attempts),
            )

        except Exception as e:
            logger.error(
                "orchestration_fatal_error",
                execution_id=str(execution_id),
                error=str(e),
            )
            try:
                await self._fail_execution(execution_id, f"Fatal orchestration error: {str(e)}")
                await self.db.commit()
            except Exception:
                pass

    async def _execute_agent_with_retry(
        self,
        agent: Any,
        agent_input: AgentInput,
        execution_id: uuid.UUID,
    ) -> AgentResult:
        """Execute an agent with automatic retry on transient failure."""
        settings = get_settings()
        max_retries = max(1, getattr(settings, "max_agent_retries", 3))
        delay = getattr(settings, "agent_retry_delay_seconds", 1.0)

        last_result: Optional[AgentResult] = None
        for attempt in range(1, max_retries + 1):
            result = await agent.safe_execute(agent_input)
            if result.success:
                await self._save_agent_run(execution_id, result)
                return result

            last_result = result
            logger.warning(
                "agent_attempt_failed_retrying",
                agent=agent.name,
                attempt=attempt,
                max_retries=max_retries,
                error=result.error,
            )
            if attempt < max_retries:
                await asyncio.sleep(delay * attempt)

        if last_result:
            await self._save_agent_run(execution_id, last_result)
            return last_result
        return AgentResult(
            agent_name=agent.name,
            agent_version=agent.version,
            success=False,
            error="Agent execution failed after retries",
        )

    async def _save_agent_run(self, execution_id: uuid.UUID, result: AgentResult) -> None:
        """Persist an agent run record."""
        status = AgentRunStatus.COMPLETED if result.success else AgentRunStatus.FAILED
        run = AgentRun(
            execution_id=execution_id,
            agent_name=result.agent_name,
            agent_version=result.agent_version,
            input_data=None,  # Don't persist full input for security
            output_data=result.output,
            status=status,
            model_provider=result.model_provider,
            latency_ms=result.latency_ms,
            token_usage=result.token_usage,
        )
        self.db.add(run)
        await self.db.commit()

    async def _fail_execution(self, execution_id: uuid.UUID, reason: str, campaign_id: uuid.UUID | None = None, campaign_name: str = "") -> None:
        """Mark execution as failed and dispatch webhook alert."""
        await self.execution_service.update_execution_state(
            execution_id,
            ExecutionStatus.FAILED,
            reason,
            failure_reason=reason,
        )
        if campaign_id:
            await self.webhook_service.send_alert(
                event_type="execution_failed",
                execution_id=execution_id,
                campaign_id=campaign_id,
                campaign_name=campaign_name,
                status="failed",
                details={"reason": reason},
            )
        logger.warning("execution_failed", execution_id=str(execution_id), reason=reason)

