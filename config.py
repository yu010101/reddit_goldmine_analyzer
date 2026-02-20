"""
Centralized configuration for Reddit Goldmine Analyzer.

Override any value via environment variables prefixed with RGA_:
    RGA_MODEL=gpt-4.1-nano  python goldmine_finder.py --url ...
"""

import os

# ── Reddit Fetcher ────────────────────────────────────────────────────────────

RATE_LIMIT_DELAY: float = float(os.environ.get("RGA_RATE_LIMIT_DELAY", "2"))
REQUEST_TIMEOUT: int = int(os.environ.get("RGA_REQUEST_TIMEOUT", "30"))
USER_AGENT: str = os.environ.get(
    "RGA_USER_AGENT",
    "RedditGoldmineAnalyzer/1.0 (Educational Research)",
)

# ── AI Analyzer ───────────────────────────────────────────────────────────────

MODEL: str = os.environ.get("RGA_MODEL", "gpt-4.1-mini")
TEMPERATURE: float = float(os.environ.get("RGA_TEMPERATURE", "0.3"))
MAX_COMMENTS: int = int(os.environ.get("RGA_MAX_COMMENTS", "100"))
MAX_COMMENTS_IN_PROMPT: int = int(os.environ.get("RGA_MAX_COMMENTS_IN_PROMPT", "50"))
