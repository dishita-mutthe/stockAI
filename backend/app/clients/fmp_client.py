"""Financial Modeling Prep client (BRD §6.1).

Free tier: 250 calls/day. Endpoints used:
  - /v3/profile/{ticker}                  market cap, sector, basics
  - /v3/income-statement/{ticker}         revenue, net income, EPS
  - /v3/ratios-ttm/{ticker}               P/E, P/S
  - /v3/cash-flow-statement/{ticker}      free cash flow
  - /v3/insider-trading?symbol={ticker}   executive buy/sell activity
"""

from __future__ import annotations

from typing import Any

import httpx

from app.config import get_settings

BASE_URL = "https://financialmodelingprep.com/api"


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
        return await self._get(f"/v3/profile/{ticker}")

    async def income_statement(self, ticker: str, limit: int = 4) -> list[dict[str, Any]]:
        return await self._get(f"/v3/income-statement/{ticker}", {"limit": limit})

    async def ratios_ttm(self, ticker: str) -> list[dict[str, Any]]:
        return await self._get(f"/v3/ratios-ttm/{ticker}")

    async def cash_flow(self, ticker: str, limit: int = 4) -> list[dict[str, Any]]:
        return await self._get(f"/v3/cash-flow-statement/{ticker}", {"limit": limit})

    async def insider_trading(self, ticker: str) -> list[dict[str, Any]]:
        return await self._get("/v4/insider-trading", {"symbol": ticker})
