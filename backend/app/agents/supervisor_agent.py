"""Supervisor Agent — BRD §6.4."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.agents.base import _safe_parse_json
from app.clients.llm_client import LLMClient
from app.models.schemas import AgentResult, FinalSignal, SupervisorResult
from app.prompts import supervisor as prompts

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Aggregates the three data agents into a final signal."""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()

    def synthesize(self, ticker: str, agent_results: list[AgentResult]) -> SupervisorResult:
        payload: list[dict[str, Any]] = [
            {
                "agent": r.agent.value,
                "signal": r.signal.value,
                "summary": r.summary,
                "error": r.error,
            }
            for r in agent_results
        ]
        user = prompts.USER_TEMPLATE.format(
            ticker=ticker,
            agent_results_json=json.dumps(payload, indent=2),
        )
        try:
            raw = self.llm.complete(system=prompts.SYSTEM, user=user)
            parsed = _safe_parse_json(raw)
            return SupervisorResult(
                ticker=ticker,
                final_signal=FinalSignal(parsed.get("final_signal", "hold")),
                rationale=parsed.get("rationale", ""),
                conflicts=list(parsed.get("conflicts", []) or []),
            )
        except Exception as exc:  # noqa: BLE001
            logger.exception("Supervisor failed for %s", ticker)
            return SupervisorResult(
                ticker=ticker,
                final_signal=FinalSignal.HOLD,
                rationale=f"Supervisor error: {exc}",
                conflicts=[],
            )
