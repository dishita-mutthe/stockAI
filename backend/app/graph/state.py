"""LangGraph state shared across nodes in the analysis workflow."""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from app.models.schemas import AgentName, AgentResult, SupervisorResult


class AnalysisState(TypedDict, total=False):
    ticker: str
    enabled_agents: list[AgentName]
    # `operator.add` lets parallel nodes append results without clobbering each other.
    agent_results: Annotated[list[AgentResult], operator.add]
    supervisor: SupervisorResult
