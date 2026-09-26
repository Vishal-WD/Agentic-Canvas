"""O&G Agentic Canvas - Brand Knowledge Base.

Versioned O&G brand rules for RAG ingestion.
Each rule has: rule_id, category, version, priority, source, content.
"""

from __future__ import annotations

BRAND_RULES = [
    # ─── Color Rules ──────────────────────────────────────────────
    {
        "rule_id": "COLOR-001",
        "category": "color",
        "version": "1.0",
        "priority": "critical",
        "source": "O&G Brand Kit",
        "content": "Deep Navy #0C2140 is the primary foundation color. Represents trust, security, authority, and foundation. Use as primary background for approximately 60% of visual space.",
    },
    {
        "rule_id": "COLOR-002",
        "category": "color",
        "version": "1.0",
        "priority": "critical",
        "source": "O&G Brand Kit",
        "content": "Orchestration Blue #16528D represents technology, intelligence, connectivity and innovation. Use for technology elements, buttons, links and highlights.",
    },
    {
        "rule_id": "COLOR-003",
        "category": "color",
        "version": "1.0",
        "priority": "critical",
        "source": "O&G Brand Kit",
        "content": "Secure Azure #2674B8 represents innovation, clarity, and forward movement. Use for innovation highlights and active states.",
    },
    {
        "rule_id": "COLOR-004",
        "category": "color",
        "version": "1.0",
        "priority": "critical",
        "source": "O&G Brand Kit",
        "content": "Guardrail Gold #D6B25A represents protection, assurance, premium quality and guardrails. Use sparingly for emphasis, CTAs, security boundaries and important actions. It is the boundary that enables safe innovation.",
    },
    {
        "rule_id": "COLOR-005",
        "category": "color",
        "version": "1.0",
        "priority": "high",
        "source": "O&G Brand Kit",
        "content": "Cloud White #F5F8FC represents clarity, transparency, simplicity and explainability. Use as primary readable text color on dark backgrounds.",
    },
    {
        "rule_id": "COLOR-006",
        "category": "color",
        "version": "1.0",
        "priority": "medium",
        "source": "O&G Brand Kit",
        "content": "Slate #5F7188 represents balance, professionalism and technical maturity. Use for secondary text and detail information.",
    },
    {
        "rule_id": "COLOR-007",
        "category": "color",
        "version": "1.0",
        "priority": "high",
        "source": "O&G Brand Kit",
        "content": "Midnight #071426 represents zero-trust, depth, resilience and strength. Use as deep background for zero-trust contexts and controlled secure environments.",
    },
    # ─── Color Hierarchy ──────────────────────────────────────────
    {
        "rule_id": "HIERARCHY-001",
        "category": "color_hierarchy",
        "version": "1.0",
        "priority": "high",
        "source": "O&G Brand Kit",
        "content": "Color hierarchy: approximately 60% O&G Deep Navy, 20% Blue family (Orchestration Blue + Secure Azure), 10% White/Neutrals (Cloud White + Slate), 10% Guardrail Gold. Gold is an accent, not the dominant UI color.",
    },
    # ─── Gradient Rules ───────────────────────────────────────────
    {
        "rule_id": "GRADIENT-001",
        "category": "gradient",
        "version": "1.0",
        "priority": "critical",
        "source": "O&G Brand Kit",
        "content": "Approved gradient pairings: Navy → Blue (#0C2140 → #16528D), Blue → Azure (#16528D → #2674B8), Navy → Gold (#0C2140 → #D6B25A), Midnight → Blue (#071426 → #16528D). No other gradient pairings are permitted.",
    },
    # ─── Visual Guidelines ────────────────────────────────────────
    {
        "rule_id": "VISUAL-001",
        "category": "visual",
        "version": "1.0",
        "priority": "high",
        "source": "O&G Brand Kit",
        "content": "Use Navy/Midnight as major backgrounds. Use Blue/Azure for technology, buttons, links and highlights. Use Gold sparingly for emphasis, CTAs and key highlights. Use White for clarity, readability and clean layouts. Maintain strong contrast for accessibility and enterprise polish.",
    },
    {
        "rule_id": "VISUAL-002",
        "category": "visual",
        "version": "1.0",
        "priority": "high",
        "source": "O&G Brand Kit",
        "content": "Avoid excessive gradients, glow, glassmorphism or decorative effects. Avoid cartoonish UI, neon cyberpunk styling, rainbow colors, excessive animations, emoji-heavy interfaces. The product must feel like a serious enterprise AI/security platform.",
    },
    {
        "rule_id": "VISUAL-003",
        "category": "visual",
        "version": "1.0",
        "priority": "medium",
        "source": "O&G Brand Kit",
        "content": "Never introduce arbitrary brand colors. Do not replace the O&G palette with generic Bootstrap/Tailwind defaults. Do not create a light-theme-first interface.",
    },
    # ─── Typography ───────────────────────────────────────────────
    {
        "rule_id": "TYPO-001",
        "category": "typography",
        "version": "1.0",
        "priority": "high",
        "source": "O&G Brand Kit",
        "content": "Use a modern clean sans-serif family such as Inter or comparable. Headings: bold/semibold. Section labels/taglines: uppercase with controlled letter spacing. Body: highly readable Cloud White on dark backgrounds. Slate for secondary text. Avoid decorative/script fonts.",
    },
    # ─── Logo Rules ───────────────────────────────────────────────
    {
        "rule_id": "LOGO-001",
        "category": "logo",
        "version": "1.0",
        "priority": "critical",
        "source": "O&G Brand Kit",
        "content": "The O&G identity uses a protective shield with circuit-node motif, central lock/security concept, bold 'O&G' text, and descriptor 'ORCHESTRATION & GUARDRAIL'. The logo must retain strong contrast on dark backgrounds. Do not redraw, distort, rotate, stretch, or recolor the logo.",
    },
    {
        "rule_id": "LOGO-002",
        "category": "logo",
        "version": "1.0",
        "priority": "high",
        "source": "O&G Brand Kit",
        "content": "Use the official O&G logo asset. The logo should be visible on campaign assets where the campaign type requires branding. Logo placement is typically top-left in dashboard/web contexts.",
    },
    # ─── Tone ─────────────────────────────────────────────────────
    {
        "rule_id": "TONE-001",
        "category": "tone",
        "version": "1.0",
        "priority": "critical",
        "source": "O&G Brand Kit",
        "content": "Tone must be enterprise, authoritative, technically mature, security-focused, professional, grounded, clear and trustworthy. Key concepts: zero-trust, resilience, transparency, protection, reliability, enterprise security, safe innovation.",
    },
    {
        "rule_id": "TONE-002",
        "category": "tone",
        "version": "1.0",
        "priority": "high",
        "source": "O&G Brand Kit",
        "content": "Never invent certifications, customers, statistics or product capabilities. Never make unsupported claims. Avoid casual, childish or hype-heavy language. Avoid exaggerated or unverifiable claims.",
    },
    # ─── Taglines ─────────────────────────────────────────────────
    {
        "rule_id": "TAGLINE-001",
        "category": "tagline",
        "version": "1.0",
        "priority": "high",
        "source": "O&G Brand Kit",
        "content": "Approved taglines: 'Orchestrate Intelligence. Protect Everything.' and 'Orchestrate. Protect. Elevate.' Brand philosophy: 'Blue builds the intelligence. Gold defines the guardrail. Navy creates the trust.'",
    },
    # ─── Application Rules ────────────────────────────────────────
    {
        "rule_id": "APP-001",
        "category": "application",
        "version": "1.0",
        "priority": "high",
        "source": "O&G Brand Kit",
        "content": "Application examples: Product UI & Dashboard (dark mode, high contrast, clean data visualization), Pitch Decks & Reports (Navy slides, Cloud White typography), Website & Landing Pages (dark theme, approved gradients, Gold CTA), GitHub & Developer Assets (technical, clean, accessible, minimal decoration).",
    },
    {
        "rule_id": "APP-002",
        "category": "application",
        "version": "1.0",
        "priority": "medium",
        "source": "O&G Brand Kit",
        "content": "Product Dashboard campaign type: dark mode, high contrast, clean data visualization, restrained Gold emphasis. Website campaign type: dark theme, approved gradients, high-visibility Gold CTA, enterprise/security positioning. Developer Assets: technical, clean, accessible, excellent code readability.",
    },
    # ─── Accessibility ────────────────────────────────────────────
    {
        "rule_id": "A11Y-001",
        "category": "accessibility",
        "version": "1.0",
        "priority": "high",
        "source": "O&G Brand Kit",
        "content": "Maintain strong WCAG-conscious contrast. Provide alt text for all visual assets. Use proper heading hierarchy (single h1 per page). Ensure readable text size. Use semantic HTML. Do not rely on color alone to communicate status.",
    },
    {
        "rule_id": "A11Y-002",
        "category": "accessibility",
        "version": "1.0",
        "priority": "medium",
        "source": "O&G Brand Kit",
        "content": "Support keyboard navigation, visible focus states, sensible tab order, accessible labels for actionable controls. Responsive design supporting desktop, tablet and mobile viewports.",
    },
]


def get_brand_rules() -> list[dict[str, str]]:
    """Return the complete O&G brand knowledge base."""
    return BRAND_RULES.copy()


def get_rules_by_category(category: str) -> list[dict[str, str]]:
    """Return brand rules filtered by category."""
    return [r for r in BRAND_RULES if r["category"] == category]
