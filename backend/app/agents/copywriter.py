"""O&G Agentic Canvas - Copywriter Agent.

Generates enterprise-grade campaign copy using brand rules and campaign context.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from app.agents.base import AgentInput, AgentResult, BaseAgent, safe_parse_json
from app.agents.llm_provider import MockLLMProvider, get_llm_provider
from app.logging_config import get_logger
from app.schemas.models import CopywriterOutput

logger = get_logger("copywriter_agent")

COPYWRITER_SYSTEM_PROMPT = """You are the O&G Enterprise Campaign Copywriter.

MISSION:
Generate concise, enterprise-grade campaign copy for the supplied campaign brief.

BRAND:
O&G = Orchestration & Guardrail.

VOICE:
- enterprise
- authoritative
- technically mature
- security-focused
- grounded
- transparent
- professional

PRINCIPLES:
- emphasize safe innovation
- emphasize resilience and protection where relevant
- avoid exaggerated/unverifiable claims
- avoid casual, childish or hype-heavy language
- never invent certifications, customers, statistics or capabilities
- never claim a feature exists unless supplied in the input

RETRIEVED BRAND RULES:
{brand_rules}

CAMPAIGN INPUT:
{campaign_input}

OUTPUT:
Return ONLY valid JSON matching this exact schema:
{{
  "headline": "string",
  "subheadline": "string",
  "value_proposition": "string",
  "cta": "string",
  "social_posts": ["string"],
  "supporting_copy": "string",
  "brand_context_used": [{{"rule_id": "string", "version": "string"}}]
}}

QUALITY:
- clear headline
- meaningful value proposition
- specific CTA
- consistent terminology
- no unsupported claims
- no unnecessary jargon

If required information is missing, use a neutral formulation or mark the field as requiring input. Do not fabricate facts."""


class CopywriterAgent(BaseAgent):
    """Generates enterprise campaign copy aligned with O&G brand guidelines."""

    name = "copywriter"
    version = "1.0"

    def get_system_prompt(self) -> str:
        return COPYWRITER_SYSTEM_PROMPT

    def get_output_schema(self) -> type[BaseModel]:
        return CopywriterOutput

    async def execute(self, input_data: AgentInput) -> AgentResult:
        """Generate campaign copy using LLM."""
        provider = get_llm_provider()

        # Format brand rules for the prompt
        brand_rules_text = "\n".join(
            f"- [{r.get('rule_id', 'N/A')}] {r.get('content', '')}"
            for r in input_data.brand_rules
        ) or "No brand rules retrieved."

        campaign_input = (
            f"Campaign Brief: {input_data.campaign_brief}\n"
            f"Campaign Type: {input_data.campaign_type}\n"
            f"Target Audience: {input_data.target_audience}"
        )

        system_prompt = self.get_system_prompt().format(
            brand_rules=brand_rules_text,
            campaign_input=campaign_input,
        )

        try:
            response = await provider.generate(
                system_prompt=system_prompt,
                user_prompt=f"Generate campaign copy for: {input_data.campaign_brief}",
                response_format={"type": "json_object"},
            )

            try:
                raw_output = safe_parse_json(response.content)
            except Exception as parse_err:
                logger.warning("copywriter_parse_fallback", error=str(parse_err))
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
            logger.error("copywriter_json_parse_error", error=str(e))
            return AgentResult(
                agent_name=self.name,
                agent_version=self.version,
                success=False,
                error=f"Failed to parse LLM response as JSON: {str(e)}",
            )
        except Exception as e:
            logger.error("copywriter_execution_error", error=str(e))
            return AgentResult(
                agent_name=self.name,
                agent_version=self.version,
                success=False,
                error=str(e),
            )
