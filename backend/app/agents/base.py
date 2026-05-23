"""Common base class for data agents."""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any

from app.clients.llm_client import LLMClient
from app.models.schemas import AgentName, AgentResult, Signal

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Each data agent fetches data, asks the LLM to classify, returns AgentResult."""

    name: AgentName

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()

    @abstractmethod
    async def collect(self, ticker: str) -> dict[str, Any]:
        """Fetch raw data for the ticker. Returns agent-specific payload."""

    @abstractmethod
    def build_prompt(self, ticker: str, payload: dict[str, Any]) -> tuple[str, str]:
        """Return (system, user) prompt strings."""

    async def run(self, ticker: str) -> AgentResult:
        started = time.perf_counter()
        try:
            payload = await self.collect(ticker)
            system, user = self.build_prompt(ticker, payload)
            raw = self.llm.complete(system=system, user=user)
            parsed = _safe_parse_json(raw)
            signal = Signal(parsed.get("signal", "neutral"))
            summary = parsed.get("summary", "")
            return AgentResult(
                agent=self.name,
                ticker=ticker,
                signal=signal,
                summary=summary,
                data={**payload, "llm_raw": raw, "llm_parsed": parsed},
            )
        except Exception as exc:  # noqa: BLE001 — agents must never crash the workflow
            logger.exception("%s failed for %s", self.name, ticker)
            return AgentResult(
                agent=self.name,
                ticker=ticker,
                signal=Signal.NEUTRAL,
                summary=f"Agent error: {exc}",
                error=str(exc),
            )
        finally:
            logger.info(
                "%s finished for %s in %.2fs",
                self.name,
                ticker,
                time.perf_counter() - started,
            )


def _safe_parse_json(raw: str) -> dict[str, Any]:
    """Best-effort JSON extraction from an LLM response."""
    raw = raw.strip()
    # Strip ```json fences if present.
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: find the first { ... } block.
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start : end + 1])
        raise
