"""O&G Agentic Canvas - Guardrail Engine.

Orchestrates deterministic validation + semantic evaluation + scoring + repair.
"""

from __future__ import annotations

from typing import Any

from app.config import get_settings
from app.guardrails.deterministic import DeterministicValidator
from app.guardrails.repair import RepairAgent
from app.guardrails.scoring import ComplianceScore, ScoringEngine
from app.guardrails.semantic import SemanticEvaluator
from app.logging_config import get_logger

logger = get_logger("guardrail_engine")


class GuardrailEngine:
    """Main guardrail engine that orchestrates all validation layers."""

    def __init__(self):
        self.deterministic = DeterministicValidator()
        self.semantic = SemanticEvaluator()
        self.scoring = ScoringEngine()
        self.repair = RepairAgent()
        self.settings = get_settings()

    async def validate(
        self,
        campaign_output: dict[str, Any],
        brand_rules: list[dict[str, Any]],
    ) -> ComplianceScore:
        """Run full validation pipeline: deterministic + semantic + scoring."""
        # 1. Deterministic validation (authoritative)
        det_result = self.deterministic.validate(campaign_output)

        # 2. Semantic evaluation (secondary)
        sem_result = await self.semantic.evaluate(
            campaign_output=campaign_output,
            brand_rules=brand_rules,
            deterministic_results=det_result.category_scores,
        )

        # 3. Compute final score
        score = self.scoring.compute(
            deterministic_result=det_result,
            semantic_score=sem_result.semantic_score,
        )

        return score

    async def validate_and_repair(
        self,
        campaign_output: dict[str, Any],
        brand_rules: list[dict[str, Any]],
    ) -> tuple[dict[str, Any], ComplianceScore, list[dict[str, Any]]]:
        """Validate, and if failing, attempt repair up to max attempts.

        Returns: (final_output, final_score, repair_attempts)
        """
        max_attempts = self.settings.max_repair_attempts
        repair_attempts: list[dict[str, Any]] = []
        current_output = campaign_output

        for attempt in range(max_attempts + 1):
            score = await self.validate(current_output, brand_rules)

            attempt_record = {
                "attempt": attempt + 1,
                "score": score.overall_score,
                "status": score.status,
                "violation_count": len(score.violations),
                "critical_violation": score.has_critical_violation,
            }

            if score.status == "passed":
                logger.info(
                    "guardrail_passed",
                    attempt=attempt + 1,
                    score=score.overall_score,
                )
                repair_attempts.append(attempt_record)
                return current_output, score, repair_attempts

            if attempt < max_attempts:
                # Attempt repair
                logger.info(
                    "guardrail_repair_attempt",
                    attempt=attempt + 1,
                    violations=len(score.violations),
                )
                attempt_record["action"] = "repair"
                repair_attempts.append(attempt_record)

                repaired = await self.repair.repair(
                    original_output=current_output,
                    violations=score.violations,
                    brand_rules=brand_rules,
                )

                if repaired:
                    current_output = repaired
                else:
                    logger.warning("repair_returned_none", attempt=attempt + 1)
                    break
            else:
                # Max attempts reached
                repair_attempts.append(attempt_record)
                logger.warning(
                    "guardrail_max_attempts_reached",
                    max_attempts=max_attempts,
                    final_score=score.overall_score,
                )

        # Final validation after all repair attempts
        final_score = await self.validate(current_output, brand_rules)
        return current_output, final_score, repair_attempts
