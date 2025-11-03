import os
import requests
from datetime import datetime, timezone
from typing import Dict, Optional, Tuple

PROVIDER = os.getenv("MOTIVATION_PROVIDER", "zenquotes").lower()

# Simple in-memory cache for the current day's quote
_CACHE: Dict[str, Dict] = {}
_CACHE_DAY: Optional[str] = None

def _today_key() -> str:
    # Use UTC for consistency; change to localtime if preferred
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")

def _fetch_zenquotes_today() -> Dict[str, str]:
    # ZenQuotes daily: https://zenquotes.io/api/today
    # Returns: [{"q": "...", "a": "...", ...}]
    r = requests.get("https://zenquotes.io/api/today", timeout=10)
    r.raise_for_status()
    data = r.json()
    if isinstance(data, list) and data:
        q = data[0]
        return {
            "text": q.get("q") or "",
            "author": q.get("a") or "Unknown",
            "source": "zenquotes",
        }
    # Fallback
    return {"text": "Keep going!", "author": "Unknown", "source": "zenquotes"}

def _fetch_quotable_random() -> Dict[str, str]:
    # Optional alternate provider: Quotable random inspirational
    # Note: Not guaranteed to be the "same quote per day" globally.
    r = requests.get(
        "https://api.quotable.io/random",
        params={"maxLength": 180, "tags": "inspirational|success|wisdom"},
        timeout=10,
    )
    r.raise_for_status()
    j = r.json()
    return {
        "text": j.get("content") or "",
        "author": j.get("author") or "Unknown",
        "source": "quotable",
    }

def get_today_quote() -> Dict[str, str]:
    global _CACHE_DAY, _CACHE
    today = _today_key()
    if _CACHE_DAY == today and "quote" in _CACHE:
        return _CACHE["quote"]

    if PROVIDER == "quotable":
        quote = _fetch_quotable_random()
    else:
        quote = _fetch_zenquotes_today()

    _CACHE_DAY = today
    _CACHE = {"quote": quote}
    return quote