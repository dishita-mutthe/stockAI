"""News Agent — News Agent FRD §4."""

from __future__ import annotations

import json
from typing import Any

from app.agents.base import BaseAgent
from app.clients.newsdata_client import NewsDataClient
from app.models.schemas import AgentName
from app.prompts import news as prompts

# Fall back to this many chars of the article body when NewsData omits a summary.
SUMMARY_FALLBACK_CHARS = 200


class NewsAgent(BaseAgent):
    name = AgentName.NEWS

    def __init__(self, news: NewsDataClient | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.news = news or NewsDataClient()

    async def collect(self, ticker: str) -> dict[str, Any]:
        # FRD §3: query the bare ticker — NewsData surfaces the associated
        # company automatically, so no ticker-to-name resolution is needed.
        response = await self.news.latest(query=ticker, size=3)
        raw_results = response.get("results", []) or []

        # Deduplicate by article URL before trimming (FRD §10 decision). Articles
        # missing a link are kept as-is — there's no key to dedupe them on.
        seen_urls: set[str] = set()
        articles: list[dict[str, Any]] = []
        for raw in raw_results:
            url = raw.get("link")
            if url:
                if url in seen_urls:
                    continue
                seen_urls.add(url)
            articles.append(_trim_article(raw))

        payload: dict[str, Any] = {
            "query": ticker,
            "article_count": len(articles),
            "articles": articles,
        }

        # 0 articles: nothing substantive to analyze, but the LLM can still emit a
        # neutral signal. Mark PARTIAL with a descriptive message (FRD §3.3 / NA-06).
        if not articles:
            payload["_status"] = "partial"
            payload["message"] = f"No recent news found for {ticker!r}."

        return payload

    def build_prompt(self, ticker: str, payload: dict[str, Any]) -> tuple[str, str]:
        # Only the trimmed articles (headlines + summaries) go to the LLM —
        # never full article bodies (FRD §8.3, token-conscious).
        return prompts.SYSTEM, prompts.USER_TEMPLATE.format(
            ticker=ticker,
            articles_json=json.dumps(payload["articles"], indent=2, default=str),
        )


def _trim_article(raw: dict[str, Any]) -> dict[str, Any]:
    """Reduce a NewsData result to the four fields the LLM needs (FRD §4.3).

    Maps NewsData's field names to ours and falls back to the first 200 chars of
    ``content`` when ``description`` (our summary) is missing (FRD §10 decision).
    """
    summary = raw.get("description")
    if not summary:
        content = raw.get("content") or ""
        summary = content[:SUMMARY_FALLBACK_CHARS]
    return {
        "title": raw.get("title"),
        "summary": summary,
        "source": raw.get("source_id"),
        "published_at": raw.get("pubDate"),
    }
