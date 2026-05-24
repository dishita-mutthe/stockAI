"""Unit tests for FundamentalsAgent covering the three FRD §5 status paths.

Every test injects mock FMP + LLM clients so nothing hits the network or
requires real API keys. ``asyncio_mode = "auto"`` (pyproject.toml) means
``async def test_...`` works without an explicit decorator.
"""

from __future__ import annotations

import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.agents.fundamentals_agent import FundamentalsAgent
from app.models.schemas import AgentStatus, Signal

# ---------- Sample FMP responses (shape mirrors what /stable/* returns) ----------

PROFILE_OK = [{"symbol": "AAPL", "companyName": "Apple Inc.", "mktCap": 3_000_000_000_000}]
INCOME_OK = [{"date": "2025-09-28", "revenue": 95_000_000_000, "netIncome": 23_000_000_000}]
EARNINGS_OK = [{"date": "2025-10-31", "epsActual": 1.64, "epsEstimated": 1.60}]
KEY_METRICS_OK = [{"date": "2025-09-28", "forwardPE": 28.5}]
CASH_FLOW_OK = [{"date": "2025-09-28", "freeCashFlow": 25_000_000_000}]


def _build_fmp_mock(**overrides) -> MagicMock:
    """Build an FMPClient mock with the happy-path payloads, overridable per test."""
    fmp = MagicMock()
    fmp.profile = AsyncMock(return_value=overrides.get("profile", PROFILE_OK))
    fmp.income_statement = AsyncMock(return_value=overrides.get("income_statement", INCOME_OK))
    fmp.earnings = AsyncMock(return_value=overrides.get("earnings", EARNINGS_OK))
    fmp.key_metrics = AsyncMock(return_value=overrides.get("key_metrics", KEY_METRICS_OK))
    fmp.cash_flow = AsyncMock(return_value=overrides.get("cash_flow", CASH_FLOW_OK))
    return fmp


def _build_llm_mock(json_text: str) -> MagicMock:
    """LLMClient.complete is sync — a plain MagicMock with return_value is enough."""
    llm = MagicMock()
    llm.complete = MagicMock(return_value=json_text)
    return llm


# ---------- The three FRD-mandated status paths ----------


async def test_success_all_endpoints_ok():
    """All 6 FMP calls succeed, LLM returns valid JSON → status=success."""
    fmp = _build_fmp_mock()
    llm = _build_llm_mock('{"signal": "bullish", "summary": "Strong revenue and FCF."}')

    agent = FundamentalsAgent(fmp=fmp, llm=llm)
    result = await agent.run("AAPL")

    assert result.status == AgentStatus.SUCCESS
    assert result.signal == Signal.BULLISH
    assert "Strong revenue" in result.summary
    assert "_fetch_errors" not in result.data
    assert result.error is None
    llm.complete.assert_called_once()


async def test_partial_when_one_endpoint_raises():
    """One endpoint failure (after retry) → status=partial, LLM still called."""
    fmp = _build_fmp_mock()
    # Simulate cash_flow failing terminally (e.g. retry exhausted).
    fmp.cash_flow = AsyncMock(
        side_effect=httpx.HTTPStatusError(
            "500 server error",
            request=httpx.Request("GET", "https://example.com"),
            response=httpx.Response(500),
        )
    )
    llm = _build_llm_mock('{"signal": "neutral", "summary": "Mixed picture."}')

    agent = FundamentalsAgent(fmp=fmp, llm=llm)
    result = await agent.run("AAPL")

    assert result.status == AgentStatus.PARTIAL
    assert result.signal == Signal.NEUTRAL
    assert "_fetch_errors" in result.data
    assert "cash_flow" in result.data["_fetch_errors"]
    # The agent should still ask the LLM to reason over the surviving 4 sources.
    llm.complete.assert_called_once()


async def test_error_short_circuits_invalid_ticker_without_llm_call():
    """Empty profile from FMP → status=error, no LLM call (FRD FA-05)."""
    fmp = _build_fmp_mock(profile=[])  # FMP signals unknown ticker with []
    llm = _build_llm_mock("should-never-run")

    agent = FundamentalsAgent(fmp=fmp, llm=llm)
    result = await agent.run("ZZZZZZ")

    assert result.status == AgentStatus.ERROR
    assert result.signal == Signal.NEUTRAL
    assert "Unknown ticker" in result.summary
    assert result.error and "Unknown ticker" in result.error
    # Critical: short-circuit must not spend LLM tokens.
    llm.complete.assert_not_called()


# ---------- Behavioral guarantees worth pinning down ----------


async def test_fetch_errors_have_apikey_redacted():
    """Apikey must never leak through _fetch_errors to the frontend."""
    leaky_url = "https://financialmodelingprep.com/stable/profile?symbol=AAPL&apikey=SECRET_KEY_123"
    fmp = _build_fmp_mock()
    fmp.cash_flow = AsyncMock(
        side_effect=httpx.HTTPStatusError(
            f"404 Not Found for url '{leaky_url}'",
            request=httpx.Request("GET", leaky_url),
            response=httpx.Response(404),
        )
    )
    llm = _build_llm_mock('{"signal": "neutral", "summary": "ok"}')

    agent = FundamentalsAgent(fmp=fmp, llm=llm)
    result = await agent.run("AAPL")

    err_text = result.data["_fetch_errors"]["cash_flow"]
    assert "SECRET_KEY_123" not in err_text
    assert "apikey=***" in err_text


async def test_profile_fetch_failure_becomes_partial_not_error():
    """When the profile call raises (not returns []), gather catches it → PARTIAL.

    Important distinction: profile == [] means "ticker doesn't exist" → ERROR.
    Profile raising means "fetch failed transiently" → PARTIAL, still try LLM.
    """
    fmp = _build_fmp_mock()
    fmp.profile = AsyncMock(side_effect=RuntimeError("boom"))
    llm = _build_llm_mock('{"signal": "neutral", "summary": "Limited data."}')

    agent = FundamentalsAgent(fmp=fmp, llm=llm)
    result = await agent.run("AAPL")

    assert result.status == AgentStatus.PARTIAL
    assert "_fetch_errors" in result.data
    assert "profile" in result.data["_fetch_errors"]
    llm.complete.assert_called_once()


async def test_llm_failure_becomes_error_status():
    """If the LLM call itself raises (auth failure, JSON parse failure, etc.) → ERROR."""
    fmp = _build_fmp_mock()
    llm = _build_llm_mock("not valid json at all")

    agent = FundamentalsAgent(fmp=fmp, llm=llm)
    result = await agent.run("AAPL")

    assert result.status == AgentStatus.ERROR
    assert result.signal == Signal.NEUTRAL
    assert result.error is not None
