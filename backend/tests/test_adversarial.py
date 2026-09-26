"""O&G Agentic Canvas - Adversarial, Failure Injection & Guardrail Matrix Tests.

Fulfills Section 31 (Adversarial / Red-Team), Section 36 (Guardrail Matrix),
and Section 37 (Failure-Injection) testing requirements.
"""

import pytest
from app.guardrails.deterministic import DeterministicValidator
from app.guardrails.engine import GuardrailEngine
from app.guardrails.scoring import ScoringEngine


class TestGuardrailMatrix:
    """Rigorous verification of the O&G Guardrail Test Matrix (Section 36)."""

    def setup_method(self):
        self.validator = DeterministicValidator()
        self.scoring = ScoringEngine()

    @pytest.mark.parametrize("color,expected_pass", [
        ("#0C2140", True),   # Deep Navy
        ("#16528D", True),   # Orchestration Blue
        ("#2674B8", True),   # Secure Azure
        ("#D6B25A", True),   # Guardrail Gold
        ("#F5F8FC", True),   # Cloud White
        ("#5F7188", True),   # Slate
        ("#071426", True),   # Midnight
        ("#FF0000", False),  # Random Red
        ("#00FF00", False),  # Random Green
        ("#E91E63", False),  # Neon Pink
        ("#123456", False),  # Arbitrary hex
    ])
    def test_color_matrix(self, color: str, expected_pass: bool):
        result = self.validator._check_colors({"test_color": color})
        if expected_pass:
            assert len(result.violations) == 0
            assert result.score == 100
        else:
            assert len(result.violations) > 0
            assert result.violations[0].rule_id == "COLOR-001"
            assert result.score < 100

    @pytest.mark.parametrize("gradient,expected_pass", [
        ("#0C2140 → #16528D", True),   # Navy → Blue
        ("#16528D → #2674B8", True),   # Blue → Azure
        ("#0C2140 → #D6B25A", True),   # Navy → Gold
        ("#071426 → #16528D", True),   # Midnight → Blue
        ("#FF0000 → #00FF00", False),  # Red to Green
        ("#0C2140 → #FF0000", False),  # Navy to Red
        ("#2674B8 → #D6B25A", False),  # Azure to Gold (not an approved pairing)
    ])
    def test_gradient_matrix(self, gradient: str, expected_pass: bool):
        result = self.validator._check_gradients({"bg_gradient": gradient})
        if expected_pass:
            assert len(result.violations) == 0
            assert result.score == 100
        else:
            assert len(result.violations) > 0
            assert result.violations[0].rule_id == "GRADIENT-001"


class TestAdversarialToneAndClaims:
    """Adversarial testing against inappropriate tone and unsupported claims."""

    def setup_method(self):
        self.validator = DeterministicValidator()

    @pytest.mark.parametrize("hype_phrase", [
        "Our product offers 100% secure protection against every threat.",
        "We are the world's best enterprise AI orchestration platform.",
        "Guaranteed results within 24 hours of deployment.",
        "Award-winning multi-agent system certified by top agencies.",
    ])
    def test_unsupported_marketing_claims_detected(self, hype_phrase: str):
        output = {"headline": hype_phrase, "logo_placement": "top-left"}
        result = self.validator._check_tone(output)
        assert len(result.violations) > 0
        assert any(v.rule_id == "TONE-002" for v in result.violations)

    @pytest.mark.parametrize("casual_phrase", [
        "This new AI engine is totally awesome and lit!",
        "OMG bro, the vibes of this agent are insane.",
        "You gonna love how cool this zero-trust setup works.",
    ])
    def test_casual_slang_detected(self, casual_phrase: str):
        output = {"body": casual_phrase, "logo_placement": "top-left"}
        result = self.validator._check_tone(output)
        assert len(result.violations) > 0
        assert any(v.rule_id == "TONE-001" for v in result.violations)


class TestCriticalOverrideAndRepairBound:
    """Section 5.3 & Section 6: Critical violation overrides numeric score; bounded repair."""

    def test_critical_logo_violation_overrides_high_score(self):
        validator = DeterministicValidator()
        scoring = ScoringEngine()

        # Output with great colors, enterprise tone, but MISSING required logo
        output = {
            "headline": "Enterprise Zero-Trust AI Security",
            "body": "Orchestrating intelligence with robust guardrails and reliable protection.",
            "background_color": "#0C2140",
            "cta_color": "#D6B25A",
            "logo_required": True,
            "logo_placement": None,  # Critical missing logo!
        }
        val_result = validator.validate(output)
        assert val_result.has_critical_violation is True

        compliance = scoring.compute(val_result, semantic_score=95.0)
        # Even if category scores are good, critical violation must enforce status = rejected
        assert compliance.status == "rejected"
        assert compliance.has_critical_violation is True

    @pytest.mark.asyncio
    async def test_repair_loop_bounded_never_infinite(self):
        """Repair loop must be bounded by MAX_REPAIR_ATTEMPTS and never loop infinitely."""
        engine = GuardrailEngine()

        # Unrepairable output with persistent violations
        output = {
            "headline": "100% secure guarantee with awesome vibes",
            "background_color": "#FF0000",
            "gradient": "#FF0000 → #00FF00",
            "logo_required": True,
            "logo_placement": None,
        }

        final_output, compliance, attempts = await engine.validate_and_repair(
            campaign_output=output,
            brand_rules=[],
        )

        assert len(attempts) <= engine.settings.max_repair_attempts + 1
        assert compliance is not None
        assert compliance.status in ("rejected", "review_required")

