"""
Outcomes validation with normalization, word caps, regex, and dosing token bans.
"""

import re
from typing import Optional
from fastapi import HTTPException


# Prohibited dosing tokens (case-insensitive)
PROHIBITED_TOKENS = re.compile(
    r"(?i)\b(\d+(\.\d+)?\s?(mg|mcg|µg|ug|g|ml|mL|IU|units|%))\b|"
    r"\b(bid|tid|qid|q\d+h|qhs|prn|po|iv|im|sc|subcut|tds|od|bd)\b"
)

# Whitelist regex for allowed characters
ALLOWED_RE = re.compile(r"^[A-Za-z0-9 ,\-]+$")

# Maximum word count
MAX_WORDS = 7


def normalize_phrase(s: str) -> str:
    """Normalize text by trimming and collapsing whitespace."""
    if not s:
        return ""
    return " ".join(s.strip().split())


def validate_phrase(field: str, s: str):
    """Validate a phrase field with all rules."""
    if not s:
        raise HTTPException(status_code=422, detail=[{"loc":["body",field],"msg":"must not be empty","type":"value_error.empty"}])

    if len(s.split()) > MAX_WORDS:
        raise HTTPException(status_code=422, detail=[{"loc":["body",field],"msg":f"must be ≤{MAX_WORDS} words","type":"value_error.word_count"}])

    if not ALLOWED_RE.match(s):
        raise HTTPException(status_code=422, detail=[{"loc":["body",field],"msg":"invalid characters","type":"value_error.regex"}])

    if PROHIBITED_TOKENS.search(s):
        raise HTTPException(status_code=422, detail=[{"loc":["body",field],"msg":"dosing/route tokens prohibited","type":"value_error.prohibited_token"}])


def trim_words(s: str, cap: int = MAX_WORDS) -> str:
    """Trim text to word limit."""
    if not s:
        return ""
    words = normalize_phrase(s).split()
    return " ".join(words[:cap])


def clamp_llm_suggestion(text: Optional[str]) -> str:
    """
    Clamp LLM suggestion to meet validation requirements.
    
    Args:
        text: LLM-generated text
        
    Returns:
        Clamped text that passes validation
    """
    if not text:
        return ""
    
    # Normalize first
    normalized = normalize(text)
    
    if not normalized:
        return ""
    
    # Truncate to 7 words
    words = normalized.split()
    if len(words) > MAX_WORDS:
        normalized = " ".join(words[:MAX_WORDS])
    
    # Remove prohibited tokens (replace with safe alternatives)
    # Remove dosing patterns first
    normalized = re.sub(PROHIBITED_DOSE, "[dosing]", normalized, flags=re.IGNORECASE)
    
    # Remove prohibited tokens
    normalized = re.sub(rf"\b{PROHIBITED_TOKENS}\b", "[medication]", normalized, flags=re.IGNORECASE)
    
    # Ensure only whitelist characters
    normalized = re.sub(r'[^A-Za-z0-9 ,\-µ%\[\]]', '', normalized)
    
    # Final normalization
    normalized = normalize(normalized)
    
    return normalized
