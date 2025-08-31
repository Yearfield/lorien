"""
Text utility functions for Lorien.
"""

import re

PHRASE_RE = re.compile(r"^[A-Za-z0-9 ,\-]+$")

def words(text: str) -> list[str]:
    """Extract words from text."""
    if not text or not text.strip():
        return []
    toks = [t for t in re.split(r"\s+", text.strip()) if t]
    return toks

def enforce_phrase_rules(text: str, max_words: int) -> str:
    """Enforce phrase rules and raise ValueError for Pydantic validation."""
    toks = words(text)
    if len(toks) > max_words:
        raise ValueError(f"must be ≤{max_words} words")
    if not PHRASE_RE.match(text):
        raise ValueError("must contain clinical tokens only (letters/numbers/space/comma/hyphen)")
    # reject obvious sentence markers
    if any(s in text for s in [".", "!", "?", ":"]) or text.lower().startswith(("hi", "hello", "thanks", "you should")):
        raise ValueError("must be a concise phrase, not a sentence")
    return text

def truncate_to_words(text: str, max_words: int) -> str:
    """Truncate text to maximum word count."""
    if not text or not text.strip():
        return ""
    words_list = words(text)
    if len(words_list) <= max_words:
        return text
    return " ".join(words_list[:max_words])

def clamp_text(s: str | None, limit: int) -> str:
    """Clamp text to character limit."""
    if not s:
        return ""
    return s[:limit] if len(s) > limit else s
