"""O&G Agentic Canvas - Deterministic Brand Guardrail Validator.

Authoritative validation of objective brand requirements.
Colors, gradients, typography, logo, tone, accessibility.
"""

from __future__ import annotations

import re
from typing import Any

from app.logging_config import get_logger

logger = get_logger("deterministic_validator")

# ─── O&G Approved Brand Constants ─────────────────────────────────

APPROVED_COLORS = {
    "#0C2140": "Deep Navy",
    "#16528D": "Orchestration Blue",
    "#2674B8": "Secure Azure",
    "#D6B25A": "Guardrail Gold",
    "#F5F8FC": "Cloud White",
    "#5F7188": "Slate",
    "#071426": "Midnight",
}

APPROVED_COLORS_LOWER = {k.lower(): v for k, v in APPROVED_COLORS.items()}

APPROVED_GRADIENTS = [
    ("#0C2140", "#16528D"),  # Navy → Blue
    ("#16528D", "#2674B8"),  # Blue → Azure
    ("#0C2140", "#D6B25A"),  # Navy → Gold
    ("#071426", "#16528D"),  # Midnight → Blue
]

APPROVED_FONT_FAMILIES = [
    "inter", "roboto", "outfit", "open sans", "source sans",
    "helvetica", "arial", "sans-serif",
]

# Tone indicators
ENTERPRISE_KEYWORDS = [
    "enterprise", "security", "protection", "resilience", "orchestration",
    "guardrail", "compliance", "zero-trust", "infrastructure", "reliable",
    "transparent", "auditable", "scalable", "robust", "mission-critical",
]

CASUAL_KEYWORDS = [
    "awesome", "amazing", "cool", "wow", "insane", "crazy", "epic",
    "lit", "fire", "vibe", "yolo", "lol", "omg", "bro", "dude",
    "gonna", "wanna", "gotta",
]

UNSUPPORTED_CLAIM_PATTERNS = [
    r"(?i)\b100%\s+(secure|safe|guaranteed|uptime)\b",
    r"(?i)\bcertified\s+by\b",
    r"(?i)\baward[\s-]winning\b",
    r"(?i)\b#1\s+(in|for)\b",
    r"(?i)\bworld['\u2019]?s?\s+(best|leading|first|only)\b",
    r"(?i)\bguaranteed\s+results?\b",
    r"(?i)\btrusted\s+by\s+\d+",
]


class Violation:
    """Represents a single brand guardrail violation."""

    def __init__(
        self,
        rule_id: str,
        severity: str,
        field: str,
        expected: str,
        actual: str,
        message: str,
        suggested_fix: str = "",
    ):
        self.rule_id = rule_id
        self.severity = severity
        self.field = field
        self.expected = expected
        self.actual = actual
        self.message = message
        self.suggested_fix = suggested_fix

    def to_dict(self) -> dict[str, str]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "field": self.field,
            "expected": self.expected,
            "actual": self.actual,
            "message": self.message,
            "suggested_fix": self.suggested_fix,
        }


class CategoryResult:
    """Result for a single guardrail category."""

    def __init__(self, category: str, score: float, violations: list[Violation]):
        self.category = category
        self.score = score
        self.violations = violations

    @property
    def has_critical(self) -> bool:
        return any(v.severity == "critical" for v in self.violations)


class DeterministicValidationResult:
    """Complete deterministic validation result."""

    def __init__(self, category_results: dict[str, CategoryResult]):
        self.category_results = category_results

    @property
    def all_violations(self) -> list[Violation]:
        violations = []
        for cr in self.category_results.values():
            violations.extend(cr.violations)
        return violations

    @property
    def has_critical_violation(self) -> bool:
        return any(cr.has_critical for cr in self.category_results.values())

    @property
    def category_scores(self) -> dict[str, float]:
        return {name: cr.score for name, cr in self.category_results.items()}


class DeterministicValidator:
    """Deterministic brand guardrail validator — authoritative for objective rules."""

    def validate(self, campaign_output: dict[str, Any]) -> DeterministicValidationResult:
        """Run all deterministic checks against the campaign output."""
        results = {}

        results["color"] = self._check_colors(campaign_output)
        results["gradient"] = self._check_gradients(campaign_output)
        results["typography"] = self._check_typography(campaign_output)
        results["logo"] = self._check_logo(campaign_output)
        results["tone"] = self._check_tone(campaign_output)
        results["accessibility"] = self._check_accessibility(campaign_output)
        results["layout"] = self._check_layout(campaign_output)

        return DeterministicValidationResult(results)

    def _extract_hex_colors(self, data: Any, path: str = "") -> list[tuple[str, str]]:
        """Recursively extract all hex color values and their field paths."""
        colors = []
        hex_pattern = re.compile(r"#[0-9A-Fa-f]{6}\b")

        if isinstance(data, dict):
            for key, value in data.items():
                field_path = f"{path}.{key}" if path else key
                if isinstance(value, str):
                    for match in hex_pattern.findall(value):
                        colors.append((match, field_path))
                else:
                    colors.extend(self._extract_hex_colors(value, field_path))
        elif isinstance(data, list):
            for i, item in enumerate(data):
                colors.extend(self._extract_hex_colors(item, f"{path}[{i}]"))
        elif isinstance(data, str):
            for match in hex_pattern.findall(data):
                colors.append((match, path))

        return colors

    def _check_colors(self, output: dict) -> CategoryResult:
        """Check all colors are from the approved O&G palette."""
        violations = []
        found_colors = self._extract_hex_colors(output)

        for color, field in found_colors:
            if color.lower() not in APPROVED_COLORS_LOWER:
                violations.append(Violation(
                    rule_id="COLOR-001",
                    severity="high",
                    field=field,
                    expected=", ".join(APPROVED_COLORS.keys()),
                    actual=color,
                    message=f"Unapproved O&G color detected: {color}",
                    suggested_fix="Replace with an approved O&G brand color.",
                ))

        # Score: 100 if no violations, deduct per violation
        score = max(0, 100 - (len(violations) * 25))
        return CategoryResult("color", score, violations)

    def _check_gradients(self, output: dict) -> CategoryResult:
        """Check all gradients use approved pairings."""
        violations = []
        gradient_pattern = re.compile(
            r"(#[0-9A-Fa-f]{6})\s*[→\->]+\s*(#[0-9A-Fa-f]{6})"
        )

        def find_gradients(data: Any, path: str = "") -> list[tuple[str, str, str]]:
            gradients = []
            if isinstance(data, dict):
                for key, value in data.items():
                    field_path = f"{path}.{key}" if path else key
                    if isinstance(value, str):
                        for match in gradient_pattern.finditer(value):
                            gradients.append((match.group(1), match.group(2), field_path))
                    else:
                        gradients.extend(find_gradients(value, field_path))
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    gradients.extend(find_gradients(item, f"{path}[{i}]"))
            elif isinstance(data, str):
                for match in gradient_pattern.finditer(data):
                    gradients.append((match.group(1), match.group(2), path))
            return gradients

        found_gradients = find_gradients(output)
        approved_lower = [(a.lower(), b.lower()) for a, b in APPROVED_GRADIENTS]

        for color1, color2, field in found_gradients:
            if (color1.lower(), color2.lower()) not in approved_lower:
                violations.append(Violation(
                    rule_id="GRADIENT-001",
                    severity="high",
                    field=field,
                    expected="Navy→Blue, Blue→Azure, Navy→Gold, Midnight→Blue",
                    actual=f"{color1} → {color2}",
                    message=f"Unapproved gradient pairing: {color1} → {color2}",
                    suggested_fix="Use one of the four approved O&G gradient pairings.",
                ))

        score = 100 if not violations else max(0, 100 - (len(violations) * 30))
        return CategoryResult("gradient", score, violations)

    def _check_typography(self, output: dict) -> CategoryResult:
        """Check typography follows O&G guidelines."""
        violations = []

        # Check for font family references
        text_content = str(output).lower()
        has_font_reference = False
        for font in APPROVED_FONT_FAMILIES:
            if font in text_content:
                has_font_reference = True
                break

        # Check heading hierarchy if layout sections exist
        sections = output.get("sections", [])
        if sections:
            hierarchy_levels = [s.get("hierarchy_level", 1) for s in sections if isinstance(s, dict)]
            if hierarchy_levels and hierarchy_levels != sorted(hierarchy_levels):
                violations.append(Violation(
                    rule_id="TYPO-001",
                    severity="medium",
                    field="sections.hierarchy_level",
                    expected="Sequential heading hierarchy (1, 2, 3...)",
                    actual=str(hierarchy_levels),
                    message="Heading hierarchy is not sequential.",
                    suggested_fix="Ensure heading levels follow a logical hierarchy.",
                ))

        score = 100 if not violations else max(0, 100 - (len(violations) * 20))
        return CategoryResult("typography", score, violations)

    def _check_logo(self, output: dict) -> CategoryResult:
        """Check logo requirements are met."""
        violations = []

        # Check if logo_required is set and logo_placement exists
        logo_required = output.get("logo_required", True)
        logo_placement = output.get("logo_placement")

        if logo_required and not logo_placement:
            violations.append(Violation(
                rule_id="LOGO-001",
                severity="critical",
                field="logo_placement",
                expected="Logo placement must be specified when logo is required",
                actual="Missing",
                message="Required logo placement is missing.",
                suggested_fix="Add logo_placement (e.g., 'top-left') to the layout.",
            ))

        score = 0 if violations else 100
        return CategoryResult("logo", score, violations)

    def _check_tone(self, output: dict) -> CategoryResult:
        """Check tone is enterprise/authoritative, not casual."""
        violations = []

        # Collect all text content
        text_parts = []
        def extract_text(data: Any):
            if isinstance(data, str):
                text_parts.append(data)
            elif isinstance(data, dict):
                for v in data.values():
                    extract_text(v)
            elif isinstance(data, list):
                for item in data:
                    extract_text(item)

        extract_text(output)
        all_text = " ".join(text_parts).lower()

        # Check for casual language
        found_casual = [word for word in CASUAL_KEYWORDS if word in all_text]
        if found_casual:
            violations.append(Violation(
                rule_id="TONE-001",
                severity="medium",
                field="copy",
                expected="Enterprise, authoritative, security-focused tone",
                actual=f"Casual language detected: {', '.join(found_casual[:5])}",
                message="Casual or inappropriate language detected in campaign copy.",
                suggested_fix="Replace casual language with enterprise-appropriate terminology.",
            ))

        # Check for unsupported claims
        for pattern in UNSUPPORTED_CLAIM_PATTERNS:
            matches = re.findall(pattern, all_text)
            if matches:
                violations.append(Violation(
                    rule_id="TONE-002",
                    severity="high",
                    field="copy",
                    expected="Only verifiable, grounded claims",
                    actual=f"Unsupported claim: {matches[0]}",
                    message="Unsupported or unverifiable claim detected.",
                    suggested_fix="Remove or rephrase the claim with verifiable information.",
                ))

        # Calculate enterprise tone score
        enterprise_count = sum(1 for kw in ENTERPRISE_KEYWORDS if kw in all_text)
        tone_bonus = min(enterprise_count * 5, 20)

        base_score = 100 - (len(violations) * 25)
        score = min(100, max(0, base_score + tone_bonus))
        return CategoryResult("tone", score, violations)

    def _check_accessibility(self, output: dict) -> CategoryResult:
        """Check accessibility metadata."""
        violations = []

        # Check for alt text in asset recommendations
        recommendations = output.get("recommendations", [])
        for i, rec in enumerate(recommendations):
            if isinstance(rec, dict):
                if not rec.get("alt_text"):
                    violations.append(Violation(
                        rule_id="A11Y-001",
                        severity="medium",
                        field=f"recommendations[{i}].alt_text",
                        expected="Descriptive alt text for visual assets",
                        actual="Missing",
                        message=f"Missing alt text for asset recommendation {i+1}.",
                        suggested_fix="Add descriptive alt text for accessibility.",
                    ))

        # Check heading hierarchy
        sections = output.get("sections", [])
        if sections:
            has_h1 = any(
                isinstance(s, dict) and s.get("hierarchy_level") == 1
                for s in sections
            )
            if not has_h1:
                violations.append(Violation(
                    rule_id="A11Y-002",
                    severity="medium",
                    field="sections",
                    expected="At least one section with hierarchy_level 1",
                    actual="No hierarchy_level 1 found",
                    message="Missing primary heading level in layout.",
                    suggested_fix="Ensure at least one section uses hierarchy_level 1.",
                ))

        score = 100 if not violations else max(0, 100 - (len(violations) * 15))
        return CategoryResult("accessibility", score, violations)

    def _check_layout(self, output: dict) -> CategoryResult:
        """Check layout follows campaign-type rules."""
        violations = []

        sections = output.get("sections", [])
        campaign_type = output.get("campaign_type", "")

        if not sections and campaign_type:
            violations.append(Violation(
                rule_id="LAYOUT-001",
                severity="high",
                field="sections",
                expected="At least one layout section",
                actual="No sections defined",
                message="Layout has no sections defined.",
                suggested_fix="Add layout sections appropriate for the campaign type.",
            ))

        # Check for required CTA section in website/landing page types
        if campaign_type in ("website", "landing_page"):
            has_cta = any(
                isinstance(s, dict) and s.get("section_type") == "cta"
                for s in sections
            )
            if not has_cta:
                violations.append(Violation(
                    rule_id="LAYOUT-002",
                    severity="medium",
                    field="sections",
                    expected="CTA section for website/landing page",
                    actual="No CTA section found",
                    message="Website/landing page layout missing dedicated CTA section.",
                    suggested_fix="Add a CTA section with Gold accent for emphasis.",
                ))

        score = 100 if not violations else max(0, 100 - (len(violations) * 20))
        return CategoryResult("layout", score, violations)
