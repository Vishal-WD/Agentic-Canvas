"""O&G Agentic Canvas - Scoring Engine Unit Tests."""

import pytest
from app.guardrails.deterministic import CategoryResult, DeterministicValidationResult, Violation
from app.guardrails.scoring import ScoringEngine


class TestScoringEngine:
    def setup_method(self):
        self.engine = ScoringEngine()

    def test_perfect_score(self):
        cat_results = {
            "color": CategoryResult("color", 100.0, []),
            "typography": CategoryResult("typography", 100.0, []),
            "logo": CategoryResult("logo", 100.0, []),
            "tone": CategoryResult("tone", 100.0, []),
            "layout": CategoryResult("layout", 100.0, []),
            "accessibility": CategoryResult("accessibility", 100.0, []),
        }
        det_result = DeterministicValidationResult(cat_results)
        result = self.engine.compute(det_result, semantic_score=100.0)

        assert result.overall_score == 100.0
        assert result.has_critical_violation is False
        assert result.status == "passed"
        assert len(result.violations) == 0

    def test_critical_violation_forces_rejected_status(self):
        critical_violation = Violation(
            rule_id="COLOR-001",
            severity="critical",
            field="background_color",
            expected="Approved O&G palette",
            actual="#FF0000",
            message="Non-approved brand color #FF0000 used",
        )
        cat_results = {
            "color": CategoryResult("color", 90.0, [critical_violation]),
            "typography": CategoryResult("typography", 100.0, []),
            "logo": CategoryResult("logo", 100.0, []),
            "tone": CategoryResult("tone", 100.0, []),
            "layout": CategoryResult("layout", 100.0, []),
            "accessibility": CategoryResult("accessibility", 100.0, []),
        }
        det_result = DeterministicValidationResult(cat_results)
        result = self.engine.compute(det_result, semantic_score=100.0)

        # Even if overall is > 90, critical violation forces rejected
        assert result.has_critical_violation is True
        assert result.status == "rejected"
        assert len(result.violations) == 1

    def test_review_required_when_below_threshold(self):
        low_violation = Violation(
            rule_id="TONE-002",
            severity="medium",
            field="headline",
            expected="Enterprise tone",
            actual="Casual wording",
            message="Tone too casual",
        )
        cat_results = {
            "color": CategoryResult("color", 70.0, [low_violation]),
            "typography": CategoryResult("typography", 70.0, []),
            "logo": CategoryResult("logo", 70.0, []),
            "tone": CategoryResult("tone", 70.0, []),
            "layout": CategoryResult("layout", 70.0, []),
            "accessibility": CategoryResult("accessibility", 70.0, []),
        }
        det_result = DeterministicValidationResult(cat_results)
        result = self.engine.compute(det_result, semantic_score=70.0)

        assert result.overall_score < 90.0
        assert result.has_critical_violation is False
        assert result.status == "review_required"
