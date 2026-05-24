"""Common base class for data agents."""

from __future__ import annotations

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Any

from app.clients.llm_client import LLMClient
from app.models.schemas import AgentName, AgentResult, AgentStatus, Signal
from app.utils.redaction import redact

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Each data agent fetches data, asks the LLM to classify, returns AgentResult."""

    name: AgentName

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()

    @abstractmethod
    async def collect(self, ticker: str) -> dict[str, Any]:
        """Fetch raw data for the ticker. Returns agent-specific payload.

        Two optional escape-hatch keys the base class understands:
          * ``_status``       — set to an AgentStatus value to override inference
                                (used by agents that detect e.g. invalid ticker).
          * ``_fetch_errors`` — dict of {source: error_string}; when non-empty
                                and ``_status`` is unset, status becomes PARTIAL.
        """

    @abstractmethod
    def build_prompt(self, ticker: str, payload: dict[str, Any]) -> tuple[str, str]:
        """Return (system, user) prompt strings."""

    async def run(self, ticker: str) -> AgentResult:
        started = time.perf_counter()
        try:
            payload = await self.collect(ticker)

            # Early bail: if the agent self-reported ERROR (e.g. invalid ticker),
            # skip the LLM call entirely — nothing to reason about, and it costs
            # tokens. Status / error message come straight from the payload.
            if payload.get("_status") == AgentStatus.ERROR.value:
                message = payload.get("_error_message", "Agent could not produce a signal.")
                logger.info("%s short-circuited for %s: %s", self.name, ticker, message)
                return AgentResult(
                    agent=self.name,
                    ticker=ticker,
                    status=AgentStatus.ERROR,
                    signal=Signal.NEUTRAL,
                    summary=message,
                    data=payload,
                    error=message,
                )

            system, user = self.build_prompt(ticker, payload)
            raw = self.llm.complete(system=system, user=user)
            parsed = _safe_parse_json(raw)
            signal = Signal(parsed.get("signal", "neutral"))
            summary = parsed.get("summary", "")
            return AgentResult(
                agent=self.name,
                ticker=ticker,
                status=_infer_status(payload),
                signal=signal,
                summary=summary,
                data={**payload, "llm_raw": raw, "llm_parsed": parsed},
            )
        except Exception as exc:  # noqa: BLE001 — agents must never crash the workflow
            logger.exception("%s failed for %s", self.name, ticker)
            # redact() strips any apikey baked into the exception string before
            # it flows out through the API response to the frontend.
            safe_message = redact(str(exc))
            return AgentResult(
                agent=self.name,
                ticker=ticker,
                status=AgentStatus.ERROR,
                signal=Signal.NEUTRAL,
                summary=f"Agent error: {safe_message}",
                error=safe_message,
            )
        finally:
            logger.info(
                "%s finished for %s in %.2fs",
                self.name,
                ticker,
                time.perf_counter() - started,
            )


def _infer_status(payload: dict[str, Any]) -> AgentStatus:
    """Resolve the agent's status from its collected payload.

    Order: explicit ``_status`` wins → ``_fetch_errors`` implies PARTIAL → SUCCESS.
    """
    if "_status" in payload:
        return AgentStatus(payload["_status"])
    if payload.get("_fetch_errors"):
        return AgentStatus.PARTIAL
    return AgentStatus.SUCCESS


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
