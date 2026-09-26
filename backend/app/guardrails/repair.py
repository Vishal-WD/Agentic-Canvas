"""O&G Agentic Canvas - Brand Repair Agent.

Repairs identified violations while preserving valid content.
"""

from __future__ import annotations

import json
from typing import Any

from app.agents.llm_provider import get_llm_provider
from app.logging_config import get_logger

logger = get_logger("repair_agent")

REPAIR_SYSTEM_PROMPT = """You are the O&G Brand Repair Agent.

OBJECTIVE:
Repair a generated campaign while changing as little valid content as possible.

ORIGINAL OUTPUT:
{original_output}

VIOLATIONS:
{violations}

BRAND RULES:
{brand_rules}

REPAIR PRINCIPLES:
1. Fix only identified violations.
2. Preserve valid content.
3. Never invent missing business facts.
4. Never weaken brand requirements.
5. Use only approved O&G colors: #0C2140, #16528D, #2674B8, #D6B25A, #F5F8FC, #5F7188, #071426
6. Use only approved gradients: Navy→Blue, Blue→Azure, Navy→Gold, Midnight→Blue
7. Preserve enterprise/security tone.
8. Return schema-valid output.
9. If a violation cannot be safely repaired, mark it for review instead of guessing.

Return ONLY the repaired structured output as valid JSON."""


class RepairAgent:
    """Repairs brand violations in campaign output."""

    name = "repair_agent"
    version = "1.0"

    async def repair(
        self,
        original_output: dict[str, Any],
        violations: list[dict[str, str]],
        brand_rules: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """Attempt to repair violations in the output.

        Returns the repaired output dict, or None if repair fails.
        """
        if not violations:
            return original_output

        provider = get_llm_provider()

        brand_rules_text = "\n".join(
            f"- [{r.get('rule_id', 'N/A')}] {r.get('content', '')}"
            for r in brand_rules
        ) or "No brand rules available."

        prompt = REPAIR_SYSTEM_PROMPT.format(
            original_output=json.dumps(original_output, indent=2),
            violations=json.dumps(violations, indent=2),
            brand_rules=brand_rules_text,
        )

        try:
            response = await provider.generate(
                system_prompt=prompt,
                user_prompt="Repair the identified violations while preserving valid content.",
                response_format={"type": "json_object"},
            )

            repaired = json.loads(response.content)

            logger.info(
                "repair_completed",
                original_violations=len(violations),
            )
            return repaired

        except json.JSONDecodeError as e:
            logger.error("repair_json_parse_error", error=str(e))
            return None
        except Exception as e:
            logger.error("repair_failed", error=str(e))
            return None
