"""O&G Agentic Canvas - Semantic Brand Evaluator.

Secondary LLM-based evaluation — does NOT override deterministic checks.
"""

from __future__ import annotations

import json
from typing import Any

from app.agents.llm_provider import get_llm_provider
from app.logging_config import get_logger
from app.schemas.models import SemanticEvaluationOutput

logger = get_logger("semantic_evaluator")

SEMANTIC_EVALUATOR_PROMPT = """You are a secondary semantic brand-compliance evaluator for O&G.

IMPORTANT:
You are NOT the sole authority for deterministic rules.

Evaluate the supplied campaign against the retrieved O&G rules.

INPUT:
CAMPAIGN:
{campaign}

RETRIEVED RULES:
{brand_rules}

DETERMINISTIC CHECK RESULTS:
{deterministic_results}

Return ONLY JSON containing:
- semantic_score (0-100)
- violations (list of objects with rule_id, severity, message, field)
- strengths (list of strings)
- status ("pass", "fail", or "review_required")
- evaluator_version ("1.0")

RULES:
- do not invent brand rules
- do not override deterministic failures
- do not mark critical violations as acceptable
- do not reward unsupported claims
- explain violations briefly and concretely
- do not reveal hidden reasoning or chain-of-thought"""


class SemanticEvaluator:
    """Secondary semantic brand compliance evaluator using LLM."""

    version = "1.0"

    async def evaluate(
        self,
        campaign_output: dict[str, Any],
        brand_rules: list[dict[str, Any]],
        deterministic_results: dict[str, Any],
    ) -> SemanticEvaluationOutput:
        """Run semantic evaluation on campaign output."""
        provider = get_llm_provider()

        brand_rules_text = "\n".join(
            f"- [{r.get('rule_id', 'N/A')}] {r.get('content', '')}"
            for r in brand_rules
        ) or "No brand rules available."

        prompt = SEMANTIC_EVALUATOR_PROMPT.format(
            campaign=json.dumps(campaign_output, indent=2),
            brand_rules=brand_rules_text,
            deterministic_results=json.dumps(deterministic_results, indent=2),
        )

        try:
            response = await provider.generate(
                system_prompt=prompt,
                user_prompt="Evaluate this campaign for brand compliance.",
                response_format={"type": "json_object"},
            )

            raw = json.loads(response.content)
            result = SemanticEvaluationOutput.model_validate(raw)

            logger.info(
                "semantic_evaluation_complete",
                score=result.semantic_score,
                status=result.status,
                violation_count=len(result.violations),
            )
            return result

        except Exception as e:
            logger.error("semantic_evaluation_failed", error=str(e))
            # On failure, return a neutral result — deterministic checks are authoritative
            return SemanticEvaluationOutput(
                semantic_score=75.0,
                violations=[],
                strengths=["Semantic evaluation unavailable — falling back to deterministic results"],
                status="review_required",
                evaluator_version=self.version,
            )
