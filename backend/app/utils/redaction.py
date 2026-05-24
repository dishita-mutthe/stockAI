"""Redact secrets from text before it leaves the backend.

Use at boundaries where strings will be serialized to API clients or otherwise
sent off-host. Local-only INFO logging can keep raw values for debugging.

Currently masks: ``apikey=<value>`` in URLs (the FMP convention). Extend
``_PATTERNS`` if we ever integrate APIs that pass secrets in different shapes.
"""

from __future__ import annotations

import re

_PATTERNS: tuple[re.Pattern[str], ...] = (
    # Match apikey=<value> in URLs. Stops at &, whitespace, or quote chars so
    # we don't eat past the end of the value into surrounding text.
    re.compile(r"(apikey=)[^&\s'\"]+", re.IGNORECASE),
)


def redact(text: str) -> str:
    """Return ``text`` with any known secrets replaced by ``***``."""
    for pat in _PATTERNS:
        text = pat.sub(r"\1***", text)
    return text
