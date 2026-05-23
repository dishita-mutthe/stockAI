"""News Agent — BRD §6.3."""

from __future__ import annotations

import json
from typing import Any

from app.agents.base import BaseAgent
from app.clients.newsdata_client import NewsDataClient
from app.models.schemas import AgentName
from app.prompts import news as prompts


class NewsAgent(BaseAgent):
    name = AgentName.NEWS

    def __init__(self, news: NewsDataClient | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.news = news or NewsDataClient()

    async def collect(self, ticker: str) -> dict[str, Any]:
        # Querying the bare ticker is noisy; in v1 we combine ticker + "stock".
        # TODO: maintain a ticker-to-company-name map for higher precision.
        response = await self.news.latest(query=f"{ticker} stock", size=10)
        articles = response.get("results", []) or []
        return {
            "query": f"{ticker} stock",
            "article_count": len(articles),
            "articles": articles,
        }

    def build_prompt(self, ticker: str, payload: dict[str, Any]) -> tuple[str, str]:
        return prompts.SYSTEM, prompts.USER_TEMPLATE.format(
            ticker=ticker,
            articles_json=json.dumps(payload["articles"], indent=2, default=str),
        )
