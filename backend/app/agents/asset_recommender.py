"""O&G Agentic Canvas - Asset Recommender Agent.

Recommends visual assets appropriate for the campaign while respecting O&G brand guidelines.
"""

from __future__ import annotations

import json
from typing import Any

from pydantic import BaseModel

from app.agents.base import AgentInput, AgentResult, BaseAgent, safe_parse_json
from app.agents.llm_provider import MockLLMProvider, get_llm_provider
from app.logging_config import get_logger
from app.schemas.models import AssetRecommenderOutput

logger = get_logger("asset_recommender_agent")

ASSET_SYSTEM_PROMPT = """You are the O&G Asset Recommendation Agent.

OBJECTIVE:
Recommend visual assets that support the campaign while respecting O&G visual guidelines.

BRAND RULES:
{brand_rules}

CAMPAIGN:
{campaign}

LAYOUT:
{layout}

REQUIREMENTS:
- recommend appropriate asset type
- provide aspect ratio
- provide visual subject description
- provide background recommendation using only approved colors
- provide gradient recommendation only from approved pairings:
  * Navy → Blue (#0C2140 → #16528D)
  * Blue → Azure (#16528D → #2674B8)
  * Navy → Gold (#0C2140 → #D6B25A)
  * Midnight → Blue (#071426 → #16528D)
- provide accessibility alt-text guidance
- avoid arbitrary colors
- avoid visual clichés unless appropriate
- never claim an asset already exists unless supplied

Return ONLY valid JSON matching this schema:
{{
  "recommendations": [
    {{
      "asset_type": "string",
      "subject": "string",
      "aspect_ratio": "string",
      "background_color": "#hex",
      "gradient": "string or null",
      "alt_text": "string",
      "brand_restrictions": ["string"]
    }}
  ],
  "campaign_type": "string",
  "brand_context_used": [{{"rule_id": "string", "version": "string"}}]
}}"""


class AssetRecommenderAgent(BaseAgent):
    """Recommends visual assets for campaigns, using only approved brand elements."""

    name = "asset_recommender"
    version = "1.0"

    def get_system_prompt(self) -> str:
        return ASSET_SYSTEM_PROMPT

    def get_output_schema(self) -> type[BaseModel]:
        return AssetRecommenderOutput

    async def execute(self, input_data: AgentInput) -> AgentResult:
        """Generate asset recommendations using LLM."""
        provider = get_llm_provider()

        brand_rules_text = "\n".join(
            f"- [{r.get('rule_id', 'N/A')}] {r.get('content', '')}"
            for r in input_data.brand_rules
        ) or "No brand rules retrieved."

        campaign_text = (
            f"Brief: {input_data.campaign_brief}\n"
            f"Type: {input_data.campaign_type}\n"
            f"Audience: {input_data.target_audience}"
        )

        layout_text = json.dumps(
            input_data.additional_context.get("layout", {}), indent=2
        )

        system_prompt = self.get_system_prompt().format(
            brand_rules=brand_rules_text,
            campaign=campaign_text,
            layout=layout_text,
        )

        try:
            response = await provider.generate(
                system_prompt=system_prompt,
                user_prompt=f"Recommend assets for: {input_data.campaign_brief}",
                response_format={"type": "json_object"},
            )

            try:
                raw_output = safe_parse_json(response.content)
            except Exception as parse_err:
                logger.warning("asset_recommender_parse_fallback", error=str(parse_err))
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
            logger.error("asset_recommender_json_error", error=str(e))
            return AgentResult(
                agent_name=self.name,
                agent_version=self.version,
                success=False,
                error=f"Failed to parse LLM response as JSON: {str(e)}",
            )
        except Exception as e:
            logger.error("asset_recommender_error", error=str(e))
            return AgentResult(
                agent_name=self.name,
                agent_version=self.version,
                success=False,
                error=str(e),
            )
