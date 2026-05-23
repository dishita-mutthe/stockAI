"""Reddit / PRAW client (BRD §6.2).

Subreddits scanned per BRD: wallstreetbets, stocks, investing, StockMarket.
"""

from __future__ import annotations

from dataclasses import dataclass

import praw

from app.config import get_settings

DEFAULT_SUBREDDITS = ("wallstreetbets", "stocks", "investing", "StockMarket")


@dataclass
class RedditPost:
    id: str
    subreddit: str
    title: str
    selftext: str
    score: int
    num_comments: int
    author_karma: int | None
    url: str


class RedditClient:
    def __init__(self) -> None:
        s = get_settings()
        self._reddit = praw.Reddit(
            client_id=s.reddit_client_id,
            client_secret=s.reddit_client_secret,
            user_agent=s.reddit_user_agent,
        )
        self._reddit.read_only = True

    def search_ticker(
        self,
        ticker: str,
        subreddits: tuple[str, ...] = DEFAULT_SUBREDDITS,
        limit_per_sub: int = 25,
        time_filter: str = "day",
    ) -> list[RedditPost]:
        """Return top posts mentioning ticker over the past 24-48h window."""
        results: list[RedditPost] = []
        for sub in subreddits:
            for submission in self._reddit.subreddit(sub).search(
                ticker, sort="top", time_filter=time_filter, limit=limit_per_sub
            ):
                author_karma: int | None = None
                try:
                    if submission.author is not None:
                        author_karma = submission.author.link_karma + submission.author.comment_karma
                except Exception:  # noqa: BLE001 — author may be deleted / suspended
                    author_karma = None
                results.append(
                    RedditPost(
                        id=submission.id,
                        subreddit=sub,
                        title=submission.title,
                        selftext=submission.selftext or "",
                        score=submission.score,
                        num_comments=submission.num_comments,
                        author_karma=author_karma,
                        url=f"https://reddit.com{submission.permalink}",
                    )
                )
        return results
