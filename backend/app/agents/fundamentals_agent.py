"""Fundamentals Agent — BRD §6.1."""

from __future__ import annotations

import json
from typing import Any

from app.agents.base import BaseAgent
from app.clients.fmp_client import FMPClient
from app.models.schemas import AgentName
from app.prompts import fundamentals as prompts


class FundamentalsAgent(BaseAgent):
    name = AgentName.FUNDAMENTALS

    def __init__(self, fmp: FMPClient | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.fmp = fmp or FMPClient()

    async def collect(self, ticker: str) -> dict[str, Any]:
        profile = await self.fmp.profile(ticker)
        income = await self.fmp.income_statement(ticker)
        ratios = await self.fmp.ratios_ttm(ticker)
        cashflow = await self.fmp.cash_flow(ticker)
        insider = await self.fmp.insider_trading(ticker)
        return {
            "profile": profile,
            "income_statement": income,
            "ratios_ttm": ratios,
            "cash_flow": cashflow,
            "insider_trading": insider[:10],  # cap payload size
        }

    def build_prompt(self, ticker: str, payload: dict[str, Any]) -> tuple[str, str]:
        return prompts.SYSTEM, prompts.USER_TEMPLATE.format(
            ticker=ticker, metrics_json=json.dumps(payload, indent=2, default=str)
        )
