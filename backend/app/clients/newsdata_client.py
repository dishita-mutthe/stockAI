"""NewsData.io client (News Agent FRD §6).

Free tier: 200 credits/day, up to 2,000 articles/day across 88k+ sources.
We use the ``/latest`` endpoint — date-range filtering (``from_date``) is a paid
archive feature, so we rely on ``/latest``'s natural recency instead.

No retry logic (FRD §6.1): any HTTP error bubbles up via ``raise_for_status`` to
the base agent's error handler, which returns an ``error`` AgentResult.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.config import get_settings

BASE_URL = "https://newsdata.io/api/1"


class NewsDataClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or get_settings().newsdata_api_key

    async def latest(
        self,
        query: str,
        language: str = "en",
        size: int = 3,
    ) -> dict[str, Any]:
        """Fetch up to ``size`` recent articles matching ``query``.

        FRD §6.2 query parameters: apikey, q, language, size. ``category`` is
        intentionally omitted — NewsData has no ``finance`` category and the
        bare-ticker query is already topical enough.
        """
        params: dict[str, Any] = {
            "apikey": self.api_key,
            "q": query,
            "language": language,
            "size": size,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{BASE_URL}/latest", params=params)
            resp.raise_for_status()
            return resp.json()
