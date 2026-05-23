"""Thin wrapper around the Anthropic Claude API used by every agent.

Per BRD §8 guardrails: agents should always prefer real data over LLM-generated
estimates; this wrapper just provides a single completion call with a system
prompt and a user message. Validation / structured parsing is the caller's
responsibility.
"""

from __future__ import annotations

from anthropic import Anthropic

from app.config import get_settings


class LLMClient:
    def __init__(self) -> None:
        s = get_settings()
        self._client = Anthropic(api_key=s.anthropic_api_key)
        self._model = s.anthropic_model

    def complete(
        self,
        *,
        system: str,
        user: str,
        max_tokens: int = 1024,
        temperature: float = 0.2,
    ) -> str:
        msg = self._client.messages.create(
            model=self._model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        # Concatenate all text blocks defensively.
        return "".join(block.text for block in msg.content if getattr(block, "type", "") == "text")
