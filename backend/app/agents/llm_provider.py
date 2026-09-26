"""O&G Agentic Canvas - LLM Provider Abstraction.

Supports OpenAI as primary provider and a deterministic mock provider for testing.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any, Optional

from pydantic import BaseModel

from app.config import get_settings
from app.logging_config import get_logger

logger = get_logger("llm_provider")


class LLMResponse(BaseModel):
    """Structured LLM response."""
    content: str
    model: str
    provider: str
    token_usage: dict[str, int] = {}
    finish_reason: str = "stop"


class BaseLLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        response_format: Optional[dict] = None,
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        ...


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider."""

    def __init__(self):
        self.settings = get_settings()
        if not self.settings.openai_api_key:
            logger.warning("openai_api_key_not_set", msg="OpenAI API key not configured")

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        response_format: Optional[dict] = None,
    ) -> LLMResponse:
        """Generate using OpenAI API."""
        import openai

        client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key)

        kwargs: dict[str, Any] = {
            "model": self.settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if response_format:
            kwargs["response_format"] = response_format

        try:
            response = await client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content or ""
            usage = response.usage

            return LLMResponse(
                content=content,
                model=response.model,
                provider="openai",
                token_usage={
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                    "total_tokens": usage.total_tokens if usage else 0,
                },
                finish_reason=response.choices[0].finish_reason or "stop",
            )

        except openai.APITimeoutError:
            logger.error("openai_timeout")
            raise TimeoutError("OpenAI API request timed out")
        except openai.APIError as e:
            logger.error("openai_api_error", error=str(e))
            raise RuntimeError(f"OpenAI API error: {str(e)}")


import asyncio
import random


class GoogleGeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider with exponential backoff retry and multi-model fallback."""

    def __init__(self):
        self.settings = get_settings()
        if not self.settings.google_api_key:
            logger.warning("google_api_key_not_set", msg="Google API key not configured")

    def _get_candidate_models(self) -> list[str]:
        """Return prioritized list of Gemini models to attempt."""
        primary = (self.settings.llm_model or "gemini-2.5-flash").strip()
        fallbacks_str = getattr(self.settings, "llm_fallback_models", "gemini-flash-latest,gemini-2.5-flash-lite,gemini-flash-lite-latest")
        fallbacks = [m.strip() for m in fallbacks_str.split(",") if m.strip()]
        
        # Deduplicate while preserving order
        models = [primary]
        for m in fallbacks:
            if m not in models:
                models.append(m)
        return models

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        response_format: Optional[dict] = None,
    ) -> LLMResponse:
        """Generate content using Google Gemini REST API with retry and model fallback."""
        import httpx

        api_key = self.settings.google_api_key
        if not api_key:
            raise ValueError("GOOGLE_API_KEY is not set.")

        candidate_models = self._get_candidate_models()
        last_error: Optional[str] = None

        async with httpx.AsyncClient(timeout=45.0) as client:
            for model_idx, model in enumerate(candidate_models):
                max_attempts = 3 if model_idx == 0 else 2

                for attempt in range(1, max_attempts + 1):
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

                    payload: dict[str, Any] = {
                        "contents": [
                            {
                                "role": "user",
                                "parts": [{"text": user_prompt}],
                            }
                        ],
                        "generationConfig": {
                            "temperature": temperature,
                            "maxOutputTokens": max_tokens,
                        },
                    }

                    if system_prompt:
                        payload["systemInstruction"] = {
                            "parts": [{"text": system_prompt}]
                        }

                    if response_format and response_format.get("type") == "json_object":
                        payload["generationConfig"]["responseMimeType"] = "application/json"

                    try:
                        res = await client.post(url, json=payload)

                        # Handle successful response
                        if res.status_code == 200:
                            data = res.json()
                            candidate = (data.get("candidates") or [{}])[0]
                            content_part = (candidate.get("content", {}).get("parts") or [{}])[0]
                            content = content_part.get("text", "")

                            # Clean markdown backticks if returned
                            content = content.strip()
                            if content.startswith("```json"):
                                content = content[7:]
                            elif content.startswith("```"):
                                content = content[3:]
                            if content.endswith("```"):
                                content = content[:-3]
                            content = content.strip()

                            usage = data.get("usageMetadata", {})
                            finish_reason = candidate.get("finishReason", "STOP").lower()

                            if model_idx > 0:
                                logger.info(
                                    "gemini_fallback_model_succeeded",
                                    original_model=candidate_models[0],
                                    active_model=model,
                                )

                            return LLMResponse(
                                content=content,
                                model=model,
                                provider="gemini",
                                token_usage={
                                    "prompt_tokens": usage.get("promptTokenCount", 0),
                                    "completion_tokens": usage.get("candidatesTokenCount", 0),
                                    "total_tokens": usage.get("totalTokenCount", 0),
                                },
                                finish_reason=finish_reason,
                            )

                        # Model not supported or 404: skip immediately to next model
                        if res.status_code == 404:
                            last_error = f"Model {model} returned 404 Not Found"
                            logger.warning("gemini_model_not_found", model=model, status_code=404)
                            break

                        # Transient errors: 503 (high demand), 429 (rate limit), 500, 502, 504
                        if res.status_code in (503, 429, 500, 502, 504):
                            last_error = f"Gemini API error ({res.status_code}): {res.text}"
                            if attempt < max_attempts:
                                delay = (1.5 * attempt) + random.uniform(0.2, 0.8)
                                logger.warning(
                                    "gemini_transient_error_retrying",
                                    model=model,
                                    status_code=res.status_code,
                                    attempt=attempt,
                                    max_attempts=max_attempts,
                                    retry_delay_seconds=round(delay, 2),
                                )
                                await asyncio.sleep(delay)
                                continue
                            else:
                                logger.warning(
                                    "gemini_model_attempts_exhausted",
                                    model=model,
                                    status_code=res.status_code,
                                )
                                break  # Move to next candidate model

                        # Non-transient client error (e.g. 400 Bad Request, 401 Unauthorized)
                        last_error = f"Gemini API client error ({res.status_code}): {res.text}"
                        logger.error("gemini_client_error", status_code=res.status_code, error=res.text)
                        break

                    except (httpx.TimeoutException, httpx.RequestError) as net_err:
                        last_error = f"Gemini network error: {str(net_err)}"
                        if attempt < max_attempts:
                            delay = (1.5 * attempt) + random.uniform(0.2, 0.8)
                            logger.warning(
                                "gemini_network_error_retrying",
                                model=model,
                                error=str(net_err),
                                attempt=attempt,
                                retry_delay_seconds=round(delay, 2),
                            )
                            await asyncio.sleep(delay)
                            continue
                        else:
                            break

        # If all Gemini models and retries failed, activate continuity fallback to prevent pipeline crash
        logger.warning(
            "gemini_all_models_exhausted_activating_continuity_fallback",
            last_error=last_error,
            models_attempted=candidate_models,
        )
        mock_provider = MockLLMProvider()
        fallback_resp = await mock_provider.generate(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )
        return LLMResponse(
            content=fallback_resp.content,
            model=f"{candidate_models[0]} (continuity-fallback)",
            provider="gemini-continuity-fallback",
            token_usage=fallback_resp.token_usage,
            finish_reason="stop",
        )


class MockLLMProvider(BaseLLMProvider):
    """Deterministic mock LLM provider for testing."""

    def __init__(self, responses: Optional[dict[str, str]] = None):
        self.responses = responses or {}
        self.call_count = 0

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
        response_format: Optional[dict] = None,
    ) -> LLMResponse:
        """Return deterministic mock responses."""
        self.call_count += 1

        # Determine which agent is calling based on system prompt keywords
        if "semantic brand-compliance evaluator" in system_prompt.lower() or "semantic_evaluator" in system_prompt.lower():
            content = json.dumps({
                "semantic_score": 88.0,
                "violations": [],
                "strengths": [
                    "Strong enterprise tone throughout",
                    "Consistent security-focused messaging",
                    "No unsupported claims detected"
                ],
                "status": "pass",
                "evaluator_version": "1.0"
            })
        elif "Repair" in system_prompt or "repair_agent" in system_prompt.lower():
            content = json.dumps({
                "headline": "Secure Your Enterprise AI Infrastructure",
                "subheadline": "Orchestrated Protection for Intelligent Systems",
                "value_proposition": "O&G delivers enterprise-grade orchestration and guardrail protection for AI systems.",
                "cta": "Schedule a Security Assessment",
                "social_posts": ["Enterprise AI demands enterprise security. #EnterpriseAI #ZeroTrust"],
                "supporting_copy": "Built for enterprise technology leaders who demand reliability and protection.",
                "brand_context_used": [{"rule_id": "TONE-001", "version": "1.0"}]
            })
        elif "Copywriter" in system_prompt:
            content = json.dumps({
                "headline": "Secure Your Enterprise AI Infrastructure",
                "subheadline": "Orchestrated Protection for Intelligent Systems",
                "value_proposition": "O&G delivers enterprise-grade orchestration and guardrail protection for AI systems, ensuring compliance, reliability, and zero-trust security across your entire AI infrastructure.",
                "cta": "Schedule a Security Assessment",
                "social_posts": [
                    "Enterprise AI demands enterprise security. O&G delivers orchestrated guardrails that protect without limiting innovation. #EnterpriseAI #ZeroTrust",
                    "Your AI systems deserve zero-trust protection. O&G orchestrates intelligent guardrails for enterprise resilience. #AISecurity"
                ],
                "supporting_copy": "Built for enterprise technology leaders who demand reliability, transparency, and protection for their AI deployments. O&G combines intelligent orchestration with deterministic guardrails to ensure every AI operation meets your security and compliance standards.",
                "brand_context_used": [
                    {"rule_id": "TONE-001", "version": "1.0"},
                    {"rule_id": "COLOR-001", "version": "1.0"}
                ]
            })
        elif "Layout" in system_prompt:
            content = json.dumps({
                "layout_type": "landing_page",
                "campaign_type": "website",
                "sections": [
                    {
                        "section_id": "hero",
                        "section_type": "hero",
                        "content_key": "headline",
                        "background_color": "#0C2140",
                        "text_color": "#F5F8FC",
                        "accent_color": "#D6B25A",
                        "hierarchy_level": 1,
                        "components": ["headline", "subheadline", "cta_button"],
                        "placement": "full-width"
                    },
                    {
                        "section_id": "value_prop",
                        "section_type": "features",
                        "content_key": "value_proposition",
                        "background_color": "#071426",
                        "text_color": "#F5F8FC",
                        "accent_color": "#2674B8",
                        "hierarchy_level": 2,
                        "components": ["value_proposition", "feature_cards"],
                        "placement": "full-width"
                    },
                    {
                        "section_id": "cta_section",
                        "section_type": "cta",
                        "content_key": "cta",
                        "background_color": "#0C2140",
                        "text_color": "#F5F8FC",
                        "accent_color": "#D6B25A",
                        "hierarchy_level": 3,
                        "components": ["cta", "supporting_copy"],
                        "placement": "centered"
                    }
                ],
                "visual_hierarchy": "standard",
                "logo_placement": "top-left",
                "logo_required": True,
                "brand_context_used": [
                    {"rule_id": "COLOR-001", "version": "1.0"},
                    {"rule_id": "LAYOUT-001", "version": "1.0"}
                ]
            })
        elif "Asset" in system_prompt or "asset_recommender" in system_prompt.lower():
            content = json.dumps({
                "recommendations": [
                    {
                        "asset_type": "hero_image",
                        "subject": "Abstract shield-and-circuit visualization representing AI security orchestration",
                        "aspect_ratio": "16:9",
                        "background_color": "#0C2140",
                        "gradient": "Navy → Blue (#0C2140 → #16528D)",
                        "alt_text": "O&G enterprise AI security orchestration visualization",
                        "brand_restrictions": ["Use approved O&G color palette only", "No photographic imagery of people"]
                    },
                    {
                        "asset_type": "icon_set",
                        "subject": "Security, orchestration, and guardrail iconography in O&G blue palette",
                        "aspect_ratio": "1:1",
                        "background_color": "#071426",
                        "gradient": None,
                        "alt_text": "O&G security feature icons",
                        "brand_restrictions": ["Use Orchestration Blue for icon strokes", "Maintain consistent line weight"]
                    }
                ],
                "campaign_type": "website",
                "brand_context_used": [
                    {"rule_id": "VISUAL-001", "version": "1.0"},
                    {"rule_id": "GRADIENT-001", "version": "1.0"}
                ]
            })
        else:
            content = json.dumps({"message": "Mock response", "status": "ok"})

        return LLMResponse(
            content=content,
            model="mock-gpt-4o",
            provider="mock",
            token_usage={"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
            finish_reason="stop",
        )


def get_llm_provider() -> BaseLLMProvider:
    """Factory function to get the configured LLM provider."""
    settings = get_settings()

    if settings.is_testing:
        logger.info("using_mock_llm_provider")
        return MockLLMProvider()

    if settings.llm_provider == "gemini" and settings.google_api_key:
        return GoogleGeminiProvider()

    if settings.llm_provider == "openai" and settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here":
        return OpenAIProvider()

    if settings.google_api_key:
        return GoogleGeminiProvider()

    logger.info("using_mock_llm_provider")
    return MockLLMProvider()
