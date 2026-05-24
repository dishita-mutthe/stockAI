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
from app.utils.redaction import redact

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
        # (Insider trading was dropped in v1; FMP's insider endpoints are paid-tier.)
        profile, income, earnings, key_metrics, cashflow = await asyncio.gather(
            self.fmp.profile(ticker),
            self.fmp.income_statement(ticker),
            self.fmp.earnings(ticker),
            self.fmp.key_metrics(ticker),
            self.fmp.cash_flow(ticker),
            return_exceptions=True,
        )

        # Invalid-ticker short-circuit (FRD FA-05): FMP returns 200 with [] for
        # /stable/profile when the symbol doesn't exist. No point spending an
        # LLM call to reason over nothing — bail with status=error.
        if not isinstance(profile, Exception) and profile == []:
            logger.info("FMP returned empty profile for %s; treating as unknown ticker", ticker)
            return {
                "_status": "error",
                "_error_message": f"Unknown ticker: {ticker!r} not found on FMP",
                "profile": [],
            }

        sources = {
            "profile": profile,
            "income_statement": income,
            "earnings": earnings,
            "key_metrics": key_metrics,
            "cash_flow": cashflow,
        }

        payload: dict[str, Any] = {}
        errors: dict[str, str] = {}
        for key, value in sources.items():
            if isinstance(value, Exception):
                # redact() strips the apikey from any URL httpx baked into the
                # exception message — that string ends up in _fetch_errors and
                # eventually in the frontend UI.
                errors[key] = redact(f"{type(value).__name__}: {value}")
                logger.warning("FMP %s failed for %s: %s", key, ticker, value)
                payload[key] = None
            else:
                payload[key] = value

        if errors:
            payload["_fetch_errors"] = errors
        return payload

    def build_prompt(self, ticker: str, payload: dict[str, Any]) -> tuple[str, str]:
        return prompts.SYSTEM, prompts.USER_TEMPLATE.format(
            ticker=ticker, metrics_json=json.dumps(payload, indent=2, default=str)
        )
