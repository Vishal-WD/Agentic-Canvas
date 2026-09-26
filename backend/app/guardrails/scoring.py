"""O&G Agentic Canvas - Compliance Scoring Engine.

Transparent, configurable weighted scoring with critical violation override.
"""

from __future__ import annotations

from typing import Any

from app.config import get_settings
from app.guardrails.deterministic import DeterministicValidationResult
from app.logging_config import get_logger

logger = get_logger("scoring")

# Default category weights (configurable)
DEFAULT_WEIGHTS = {
    "color": 0.20,
    "typography": 0.10,
    "logo": 0.15,
    "tone": 0.15,
    "layout": 0.15,
    "accessibility": 0.15,
    "semantic": 0.10,
}


class ComplianceScore:
    """Final compliance score with critical violation override."""

    def __init__(
        self,
        overall_score: float,
        category_scores: dict[str, float],
        has_critical_violation: bool,
        status: str,
        violations: list[dict[str, str]],
    ):
        self.overall_score = overall_score
        self.category_scores = category_scores
        self.has_critical_violation = has_critical_violation
        self.status = status
        self.violations = violations

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_score": round(self.overall_score, 1),
            "category_scores": {k: round(v, 1) for k, v in self.category_scores.items()},
            "has_critical_violation": self.has_critical_violation,
            "status": self.status,
            "violation_count": len(self.violations),
        }


class ScoringEngine:
    """Computes weighted compliance scores with critical violation override."""

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        settings = get_settings()
        self.pass_threshold = settings.guardrail_pass_threshold

    def compute(
        self,
        deterministic_result: DeterministicValidationResult,
        semantic_score: float = 100.0,
    ) -> ComplianceScore:
        """Compute the final compliance score."""
        category_scores = deterministic_result.category_scores.copy()
        category_scores["semantic"] = semantic_score

        # Weighted score calculation
        overall = 0.0
        for category, weight in self.weights.items():
            score = category_scores.get(category, 100.0)
            overall += score * weight

        # Collect all violations
        all_violations = [v.to_dict() for v in deterministic_result.all_violations]

        # Critical violation override — a critical violation forces REJECTED regardless of score
        has_critical = deterministic_result.has_critical_violation

        if has_critical:
            status = "rejected"
        elif overall >= self.pass_threshold:
            status = "passed"
        else:
            status = "review_required"

        logger.info(
            "compliance_score_computed",
            overall_score=round(overall, 1),
            has_critical=has_critical,
            status=status,
            violation_count=len(all_violations),
        )

        return ComplianceScore(
            overall_score=overall,
            category_scores=category_scores,
            has_critical_violation=has_critical,
            status=status,
            violations=all_violations,
        )
