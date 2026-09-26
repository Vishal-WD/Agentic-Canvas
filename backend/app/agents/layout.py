"""O&G Agentic Canvas - Layout Structurer Agent.

Converts campaign content into a semantic, structured layout specification.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from app.agents.base import AgentInput, AgentResult, BaseAgent, safe_parse_json
from app.agents.llm_provider import MockLLMProvider, get_llm_provider
from app.logging_config import get_logger
from app.schemas.models import LayoutOutput

logger = get_logger("layout_agent")

LAYOUT_SYSTEM_PROMPT = """You are the O&G Layout Structure Agent.

OBJECTIVE:
Convert campaign content into a semantic, structured layout specification.

BRAND RULES:
{brand_rules}

CAMPAIGN TYPE:
{campaign_type}

COPY:
{copy}

RULES:
- prioritize hierarchy and readability
- use approved O&G visual language
- prefer Deep Navy (#0C2140) / Midnight (#071426) backgrounds
- use blue family (#16528D, #2674B8) for technology hierarchy
- use Gold (#D6B25A) sparingly for emphasis/CTA
- use Cloud White (#F5F8FC) for primary text
- use Slate (#5F7188) for secondary details
- follow campaign-type-specific rules
- never invent unsupported components

Return ONLY valid JSON matching this schema:
{{
  "layout_type": "string",
  "campaign_type": "string",
  "sections": [
    {{
      "section_id": "string",
      "section_type": "string",
      "content_key": "string",
      "background_color": "#hex",
      "text_color": "#hex",
      "accent_color": "#hex or null",
      "hierarchy_level": 1-5,
      "components": ["string"],
      "placement": "string"
    }}
  ],
  "visual_hierarchy": "string",
  "logo_placement": "string",
  "logo_required": true,
  "brand_context_used": [{{"rule_id": "string", "version": "string"}}]
}}

Do not generate arbitrary HTML.
Do not generate CSS.
Do not expose chain-of-thought."""


class LayoutAgent(BaseAgent):
    """Generates semantic layout specifications for campaigns."""

    name = "layout_structurer"
    version = "1.0"

    def get_system_prompt(self) -> str:
        return LAYOUT_SYSTEM_PROMPT

    def get_output_schema(self) -> type[BaseModel]:
        return LayoutOutput

    async def execute(self, input_data: AgentInput) -> AgentResult:
        """Generate layout structure using LLM."""
        provider = get_llm_provider()

        brand_rules_text = "\n".join(
            f"- [{r.get('rule_id', 'N/A')}] {r.get('content', '')}"
            for r in input_data.brand_rules
        ) or "No brand rules retrieved."

        copy_text = json.dumps(input_data.additional_context.get("copy", {}), indent=2)

        system_prompt = self.get_system_prompt().format(
            brand_rules=brand_rules_text,
            campaign_type=input_data.campaign_type,
            copy=copy_text,
        )

        try:
            response = await provider.generate(
                system_prompt=system_prompt,
                user_prompt=f"Create a layout for campaign type: {input_data.campaign_type}",
                response_format={"type": "json_object"},
            )

            try:
                raw_output = safe_parse_json(response.content)
            except Exception as parse_err:
                logger.warning("layout_parse_fallback", error=str(parse_err))
                mock_resp = await MockLLMProvider().generate(system_prompt=system_prompt, user_prompt="")
                raw_output = json.loads(mock_resp.content)

            validated = self.validate_output(raw_output)

            return AgentResult(
                agent_name=self.name,
                agent_version=self.version,
                success=True,
                output=validated.model_dump(),
                model_provider=response.provider,
                token_usage=response.token_usage,
            )

        except json.JSONDecodeError as e:
            logger.error("layout_json_parse_error", error=str(e))
            return AgentResult(
                agent_name=self.name,
                agent_version=self.version,
                success=False,
                error=f"Failed to parse LLM response as JSON: {str(e)}",
            )
        except Exception as e:
            logger.error("layout_execution_error", error=str(e))
            return AgentResult(
                agent_name=self.name,
                agent_version=self.version,
                success=False,
                error=str(e),
            )
