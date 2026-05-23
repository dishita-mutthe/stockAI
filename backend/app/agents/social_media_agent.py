"""Social Media Agent — BRD §6.2 (Reddit only in v1)."""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict
from typing import Any

from app.agents.base import BaseAgent
from app.clients.reddit_client import RedditClient
from app.models.schemas import AgentName
from app.prompts import social_media as prompts


class SocialMediaAgent(BaseAgent):
    name = AgentName.SOCIAL_MEDIA

    def __init__(self, reddit: RedditClient | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.reddit = reddit or RedditClient()

    async def collect(self, ticker: str) -> dict[str, Any]:
        # PRAW is synchronous; offload to a thread so we don't block the loop.
        posts = await asyncio.to_thread(self.reddit.search_ticker, ticker)
        # Sort by score so the prompt sees the most influential posts first.
        posts.sort(key=lambda p: p.score, reverse=True)
        return {
            "window": "24-48h",
            "post_count": len(posts),
            "top_posts": [asdict(p) for p in posts[:20]],
        }

    def build_prompt(self, ticker: str, payload: dict[str, Any]) -> tuple[str, str]:
        return prompts.SYSTEM, prompts.USER_TEMPLATE.format(
            ticker=ticker,
            window=payload["window"],
            posts_json=json.dumps(payload["top_posts"], indent=2, default=str),
        )
