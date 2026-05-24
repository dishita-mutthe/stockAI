"""Fundamentals Agent — BRD §6.1."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from app.agents.base import BaseAgent
from app.clients.fmp_client import FMPClient
from app.models.schemas import AgentName
from app.prompts import fundamentals as prompts

logger = logging.getLogger(__name__)


class FundamentalsAgent(BaseAgent):
    name = AgentName.FUNDAMENTALS

    def __init__(self, fmp: FMPClient | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.fmp = fmp or FMPClient()

    async def collect(self, ticker: str) -> dict[str, Any]:
        # Fan out the 5 FMP calls in parallel. return_exceptions=True keeps a
        # single bad endpoint (e.g. a renamed /stable/ slug) from killing the
        # whole agent — the LLM can still reason over whatever fields succeeded.
        profile, income, ratios, cashflow, insider = await asyncio.gather(
            self.fmp.profile(ticker),
            self.fmp.income_statement(ticker),
            self.fmp.ratios_ttm(ticker),
            self.fmp.cash_flow(ticker),
            self.fmp.insider_trading(ticker),
            return_exceptions=True,
        )

        sources = {
            "profile": profile,
            "income_statement": income,
            "ratios_ttm": ratios,
            "cash_flow": cashflow,
            "insider_trading": insider,
        }

        payload: dict[str, Any] = {}
        errors: dict[str, str] = {}
        for key, value in sources.items():
            if isinstance(value, Exception):
                errors[key] = f"{type(value).__name__}: {value}"
                logger.warning("FMP %s failed for %s: %s", key, ticker, value)
                payload[key] = None
            else:
                payload[key] = value[:10] if key == "insider_trading" else value

        if errors:
            payload["_fetch_errors"] = errors
        return payload

    def build_prompt(self, ticker: str, payload: dict[str, Any]) -> tuple[str, str]:
        return prompts.SYSTEM, prompts.USER_TEMPLATE.format(
            ticker=ticker, metrics_json=json.dumps(payload, indent=2, default=str)
        )
