"""O&G Agentic Canvas - Base Agent Interface.

All agents must implement this interface for consistent behavior,
validation, logging, and error handling.
"""

from __future__ import annotations

import json
import re
import time
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ValidationError

from app.logging_config import get_logger

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)

logger = get_logger("agent_base")


def safe_parse_json(content: str) -> dict[str, Any]:
    """Robustly parse JSON from LLM outputs, stripping fences and handling syntax quirks."""
    text = content.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except Exception:
        # Extract enclosing JSON object
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            snippet = text[start : end + 1]
            try:
                return json.loads(snippet)
            except Exception:
                # Remove trailing commas
                cleaned = re.sub(r",\s*([\]}])", r"\1", snippet)
                try:
                    return json.loads(cleaned)
                except Exception:
                    pass
        raise



class AgentInput(BaseModel):
    """Base input for all agents."""
    campaign_brief: str
    campaign_type: str
    target_audience: str
    brand_rules: list[dict[str, Any]] = []
    additional_context: dict[str, Any] = {}


class AgentResult(BaseModel):
    """Wrapper for agent execution results."""
    agent_name: str
    agent_version: str
    success: bool
    output: dict[str, Any] | None = None
    error: str | None = None
    latency_ms: float = 0
    model_provider: str | None = None
    token_usage: dict[str, int] | None = None


class BaseAgent(ABC):
    """Abstract base class for all O&G agents."""

    name: str = "base_agent"
    version: str = "1.0"

    @abstractmethod
    async def execute(self, input_data: AgentInput) -> AgentResult:
        """Execute the agent's task and return a validated result."""
        ...

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent."""
        ...

    @abstractmethod
    def get_output_schema(self) -> type[BaseModel]:
        """Return the Pydantic model for output validation."""
        ...

    def validate_output(self, raw_output: dict[str, Any]) -> BaseModel:
        """Validate raw output against the agent's output schema."""
        schema = self.get_output_schema()
        return schema.model_validate(raw_output)

    async def safe_execute(self, input_data: AgentInput) -> AgentResult:
        """Execute with timing, validation, and error handling."""
        start_time = time.time()

        try:
            result = await self.execute(input_data)
            result.latency_ms = (time.time() - start_time) * 1000

            logger.info(
                "agent_execution_complete",
                agent=self.name,
                version=self.version,
                success=result.success,
                latency_ms=round(result.latency_ms, 2),
            )
            return result

        except ValidationError as e:
            latency = (time.time() - start_time) * 1000
            logger.error(
                "agent_output_validation_failed",
                agent=self.name,
                error=str(e),
                latency_ms=round(latency, 2),
            )
            return AgentResult(
                agent_name=self.name,
                agent_version=self.version,
                success=False,
                error=f"Output validation failed: {str(e)}",
                latency_ms=latency,
            )

        except Exception as e:
            latency = (time.time() - start_time) * 1000
            logger.error(
                "agent_execution_failed",
                agent=self.name,
                error=str(e),
                latency_ms=round(latency, 2),
            )
            return AgentResult(
                agent_name=self.name,
                agent_version=self.version,
                success=False,
                error=f"Agent execution failed: {str(e)}",
                latency_ms=latency,
            )
