"""Supervisor Agent — BRD §6.4."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.agents.base import _safe_parse_json
from app.clients.llm_client import LLMClient
from app.models.schemas import AgentResult, AgentStatus, FinalSignal, SupervisorResult
from app.prompts import supervisor as prompts

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Aggregates the three data agents into a final signal."""

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()

    def synthesize(self, ticker: str, agent_results: list[AgentResult]) -> SupervisorResult:
        # If every data agent errored (e.g. invalid ticker), there is nothing
        # to synthesize. Skip the LLM call and surface the agent failures
        # directly to the user.
        if agent_results and all(r.status == AgentStatus.ERROR for r in agent_results):
            messages = [f"{r.agent.value}: {r.error or r.summary}" for r in agent_results]
            logger.info("Supervisor short-circuited for %s — all agents errored", ticker)
            return SupervisorResult(
                ticker=ticker,
                final_signal=FinalSignal.HOLD,
                rationale=(
                    "No signal could be produced — every data agent errored. "
                    "See per-agent details below."
                ),
                conflicts=messages,
            )

        payload: list[dict[str, Any]] = [
            {
                "agent": r.agent.value,
                "status": r.status.value,
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
