"""NewsData.io client (BRD §6.3).

Free tier: 200 credits/day, up to 2,000 articles/day across 88k+ sources.
Provides built-in AI sentiment / tags / summaries / event categorization.
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
        category: str = "business",
        language: str = "en",
        size: int = 10,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "apikey": self.api_key,
            "q": query,
            "category": category,
            "language": language,
            "size": size,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{BASE_URL}/latest", params=params)
            resp.raise_for_status()
            return resp.json()
