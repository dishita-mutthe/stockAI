"""Pydantic request/response models shared between API and agents."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AgentName(str, Enum):
    FUNDAMENTALS = "fundamentals"
    SOCIAL_MEDIA = "social_media"
    NEWS = "news"


class Signal(str, Enum):
    """Per-agent signal (BRD §6)."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class FinalSignal(str, Enum):
    """Supervisor's synthesized signal (BRD §6.4)."""

    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    BUY_WITH_CAUTION = "buy_with_caution"
    SELL_WITH_CAUTION = "sell_with_caution"


class AnalysisRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, examples=["AAPL"])
    agents: list[AgentName] = Field(
        default_factory=lambda: list(AgentName),
        description="Which data agents to include in this run.",
    )


class AgentResult(BaseModel):
    """Common envelope returned by every data agent."""

    agent: AgentName
    ticker: str
    signal: Signal
    summary: str
    data: dict[str, Any] = Field(
        default_factory=dict,
        description="Agent-specific payload (metrics, top posts, articles, ...).",
    )
    error: str | None = None


class SupervisorResult(BaseModel):
    ticker: str
    final_signal: FinalSignal
    rationale: str
    conflicts: list[str] = Field(default_factory=list)


class AnalysisResponse(BaseModel):
    ticker: str
    started_at: datetime
    completed_at: datetime
    agent_results: list[AgentResult]
    supervisor: SupervisorResult
    disclaimer: str = (
        "StockAI outputs are not financial advice. Verify independently before "
        "making investment decisions."
    )
