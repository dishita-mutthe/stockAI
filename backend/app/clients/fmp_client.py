"""Financial Modeling Prep client (BRD §6.1).

NOTE: FMP deprecated the /api/v3/* paths on Aug 31, 2025 for new accounts and
moved everyone to the /stable/* API. Path-style symbols (/profile/AAPL) are
gone — everything is now ?symbol=AAPL query params.

Free tier: 250 calls/day. Endpoints used:
  - /stable/profile?symbol={t}                market cap, sector, basics
  - /stable/income-statement?symbol={t}       revenue, net income, EPS
  - /stable/earnings?symbol={t}               EPS actual vs estimate
  - /stable/key-metrics?symbol={t}            forward P/E
  - /stable/cash-flow-statement?symbol={t}    free cash flow

Insider trading was dropped from v1 — FMP's insider endpoints are paid-tier
only. Reconsider for v2 if we upgrade or find a free alternative.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

BASE_URL = "https://financialmodelingprep.com"
RETRY_DELAY_SECONDS = 2.0
RETRIABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


def _is_retriable(exc: httpx.HTTPStatusError | httpx.RequestError) -> bool:
    """Per FRD §6: retry on 429 / 5xx, plus transient network errors."""
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRIABLE_STATUS_CODES
    # httpx.RequestError covers timeouts, connection refused, DNS failures.
    return True


class FMPClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or get_settings().fmp_api_key

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET with retry-once-after-2s on 429 / 5xx / network errors (FRD §6)."""
        params = {**(params or {}), "apikey": self.api_key}
        last_exc: Exception | None = None
        for attempt in (1, 2):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    resp = await client.get(f"{BASE_URL}{path}", params=params)
                    resp.raise_for_status()
                    return resp.json()
            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                last_exc = exc
                if attempt == 2 or not _is_retriable(exc):
                    raise
                logger.warning(
                    "FMP %s attempt %d failed (%s); retrying in %.1fs",
                    path,
                    attempt,
                    exc,
                    RETRY_DELAY_SECONDS,
                )
                await asyncio.sleep(RETRY_DELAY_SECONDS)
        # Unreachable — the loop either returns, raises, or sleeps then loops.
        assert last_exc is not None
        raise last_exc

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
