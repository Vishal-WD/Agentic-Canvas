"""O&G Agentic Canvas - Guardrail Unit Tests.

Tests the deterministic validator against the O&G guardrail test matrix.
"""

import pytest
from app.guardrails.deterministic import DeterministicValidator
from app.guardrails.scoring import ScoringEngine


class TestColorGuardrails:
    """Test color validation against O&G approved palette."""

    def setup_method(self):
        self.validator = DeterministicValidator()

    def test_deep_navy_passes(self):
        output = {"background_color": "#0C2140"}
        result = self.validator._check_colors(output)
        assert result.score == 100
        assert len(result.violations) == 0

    def test_orchestration_blue_passes(self):
        output = {"accent_color": "#16528D"}
        result = self.validator._check_colors(output)
        assert result.score == 100

    def test_secure_azure_passes(self):
        output = {"highlight": "#2674B8"}
        result = self.validator._check_colors(output)
        assert result.score == 100

    def test_guardrail_gold_passes(self):
        output = {"cta_color": "#D6B25A"}
        result = self.validator._check_colors(output)
        assert result.score == 100

    def test_cloud_white_passes(self):
        output = {"text_color": "#F5F8FC"}
        result = self.validator._check_colors(output)
        assert result.score == 100

    def test_slate_passes(self):
        output = {"secondary": "#5F7188"}
        result = self.validator._check_colors(output)
        assert result.score == 100

    def test_midnight_passes(self):
        output = {"bg": "#071426"}
        result = self.validator._check_colors(output)
        assert result.score == 100

    def test_red_fails(self):
        output = {"background_color": "#FF0000"}
        result = self.validator._check_colors(output)
        assert result.score < 100
        assert len(result.violations) > 0
        assert result.violations[0].rule_id == "COLOR-001"

    def test_random_green_fails(self):
        output = {"accent": "#00FF00"}
        result = self.validator._check_colors(output)
        assert result.score < 100
        assert len(result.violations) > 0

    def test_case_insensitive_color_passes(self):
        output = {"bg": "#0c2140"}
        result = self.validator._check_colors(output)
        assert result.score == 100


class TestGradientGuardrails:
    """Test gradient validation against approved pairings."""

    def setup_method(self):
        self.validator = DeterministicValidator()

    def test_navy_to_blue_passes(self):
        output = {"gradient": "Navy → Blue (#0C2140 → #16528D)"}
        result = self.validator._check_gradients(output)
        assert result.score == 100

    def test_blue_to_azure_passes(self):
        output = {"gradient": "#16528D → #2674B8"}
        result = self.validator._check_gradients(output)
        assert result.score == 100

    def test_navy_to_gold_passes(self):
        output = {"gradient": "#0C2140 → #D6B25A"}
        result = self.validator._check_gradients(output)
        assert result.score == 100

    def test_midnight_to_blue_passes(self):
        output = {"gradient": "#071426 → #16528D"}
        result = self.validator._check_gradients(output)
        assert result.score == 100

    def test_unapproved_gradient_fails(self):
        output = {"gradient": "#FF0000 → #00FF00"}
        result = self.validator._check_gradients(output)
        assert result.score < 100
        assert len(result.violations) > 0


class TestToneGuardrails:
    """Test tone validation."""

    def setup_method(self):
        self.validator = DeterministicValidator()

    def test_enterprise_tone_passes(self):
        output = {
            "headline": "Secure Your Enterprise AI Infrastructure",
            "value_proposition": "Enterprise-grade orchestration and protection for AI systems",
        }
        result = self.validator._check_tone(output)
        assert result.score >= 80

    def test_casual_tone_fails(self):
        output = {
            "headline": "This awesome product is gonna blow your mind!",
            "value_proposition": "OMG it's so cool and amazing, dude!",
        }
        result = self.validator._check_tone(output)
        assert len(result.violations) > 0

    def test_unsupported_claim_fails(self):
        output = {
            "headline": "World's Best AI Security Platform",
            "value_proposition": "Trusted by 10000 enterprises. 100% guaranteed uptime.",
        }
        result = self.validator._check_tone(output)
        assert any(v.rule_id == "TONE-002" for v in result.violations)


class TestLogoGuardrails:
    """Test logo requirement checks."""

    def setup_method(self):
        self.validator = DeterministicValidator()

    def test_logo_present_passes(self):
        output = {"logo_required": True, "logo_placement": "top-left"}
        result = self.validator._check_logo(output)
        assert result.score == 100

    def test_missing_required_logo_fails(self):
        output = {"logo_required": True}
        result = self.validator._check_logo(output)
        assert result.score == 0
        assert result.has_critical
        assert result.violations[0].severity == "critical"


class TestScoringEngine:
    """Test compliance scoring with critical violation override."""

    def setup_method(self):
        self.validator = DeterministicValidator()
        self.scorer = ScoringEngine()

    def test_critical_violation_overrides_high_score(self):
        """Score 99 + critical violation = REJECTED."""
        output = {
            "headline": "Secure Enterprise AI",
            "background_color": "#0C2140",
            "text_color": "#F5F8FC",
            "logo_required": True,
            # Missing logo_placement — critical violation
        }
        det_result = self.validator.validate(output)
        score = self.scorer.compute(det_result, semantic_score=99)

        assert score.has_critical_violation
        assert score.status == "rejected"

    def test_all_passing_gives_approved(self):
        output = {
            "headline": "Enterprise AI Security Platform",
            "background_color": "#0C2140",
            "text_color": "#F5F8FC",
            "logo_required": True,
            "logo_placement": "top-left",
            "sections": [
                {"hierarchy_level": 1, "section_type": "hero"},
                {"hierarchy_level": 2, "section_type": "features"},
                {"hierarchy_level": 3, "section_type": "cta"},
            ],
        }
        det_result = self.validator.validate(output)
        score = self.scorer.compute(det_result, semantic_score=90)

        assert not score.has_critical_violation
        assert score.status == "passed"
        assert score.overall_score >= 75


class TestFullValidation:
    """End-to-end validation tests."""

    def setup_method(self):
        self.validator = DeterministicValidator()

    def test_full_valid_campaign(self):
        output = {
            "headline": "Secure Your Enterprise AI Infrastructure",
            "subheadline": "Orchestrated Protection for Intelligent Systems",
            "value_proposition": "Enterprise-grade orchestration and guardrail protection",
            "cta": "Schedule a Security Assessment",
            "background_color": "#0C2140",
            "text_color": "#F5F8FC",
            "accent_color": "#D6B25A",
            "logo_required": True,
            "logo_placement": "top-left",
            "campaign_type": "website",
            "sections": [
                {"section_id": "hero", "section_type": "hero", "hierarchy_level": 1},
                {"section_id": "features", "section_type": "features", "hierarchy_level": 2},
                {"section_id": "cta", "section_type": "cta", "hierarchy_level": 3},
            ],
            "recommendations": [
                {"alt_text": "O&G security visualization", "asset_type": "hero_image"}
            ],
        }
        result = self.validator.validate(output)
        assert not result.has_critical_violation

    def test_campaign_with_bad_colors(self):
        output = {
            "headline": "Enterprise Security",
            "background_color": "#FF0000",
            "accent_color": "#00FF00",
            "logo_required": True,
            "logo_placement": "top-left",
        }
        result = self.validator.validate(output)
        color_result = result.category_results["color"]
        assert len(color_result.violations) == 2
