"""Financial Modeling Prep client (BRD §6.1).

NOTE: FMP deprecated the /api/v3/* paths on Aug 31, 2025 for new accounts and
moved everyone to the /stable/* API. Path-style symbols (/profile/AAPL) are
gone — everything is now ?symbol=AAPL query params.

Free tier: 250 calls/day. Endpoints used:
  - /stable/profile?symbol={t}                market cap, sector, basics
  - /stable/income-statement?symbol={t}       revenue, net income, EPS
  - /stable/earnings?symbol={t}               EPS actual vs estimate
  - /stable/key-metrics?symbol={t}            Forward PE
  - /stable/cash-flow-statement?symbol={t}    free cash flow
  - /stable/insider-trading-search?symbol={t} executive buy/sell activity
"""

from __future__ import annotations

from typing import Any

import httpx

from app.config import get_settings

BASE_URL = "https://financialmodelingprep.com"


class FMPClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or get_settings().fmp_api_key

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        params = {**(params or {}), "apikey": self.api_key}
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{BASE_URL}{path}", params=params)
            resp.raise_for_status()
            return resp.json()

    async def profile(self, ticker: str) -> list[dict[str, Any]]:
        return await self._get("/stable/profile", {"symbol": ticker})

    async def income_statement(self, ticker: str, limit: int = 4) -> list[dict[str, Any]]:
        return await self._get("/stable/income-statement", {"symbol": ticker, "limit": limit})

    async def earnings(self, ticker: str, limit: int = 4) -> list[dict[str, Any]]:
        return await self._get("/stable/earnings", {"symbol": ticker, "limit": limit})

    async def key_metrics(self, ticker: str, limit: int = 4) -> list[dict[str, Any]]:
        return await self._get("/stable/key-metrics", {"symbol": ticker, "limit": limit})

    async def cash_flow(self, ticker: str, limit: int = 4) -> list[dict[str, Any]]:
        return await self._get(
            "/stable/cash-flow-statement", {"symbol": ticker, "limit": limit}
        )

    async def insider_trading(self, ticker: str) -> list[dict[str, Any]]:
        return await self._get("/stable/insider-trading-search", {"symbol": ticker})
