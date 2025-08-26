from __future__ import annotations
import json
import re
from typing import Any, Dict, Tuple

JSON_OBJ_RE = re.compile(r"\{.*\}", re.DOTALL)

def extract_first_json(s: str) -> str | None:
    """Extracts the first {...} block; naive but effective for short outputs."""
    m = JSON_OBJ_RE.search(s)
    return m.group(0) if m else None

def parse_fill_response(s: str) -> Tuple[str, str]:
    """
    Returns (diagnostic_triage, actions). Missing keys become empty strings.
    """
    j = extract_first_json(s) or "{}"
    try:
        obj = json.loads(j)
    except Exception:
        obj = {}
    dt = (obj.get("diagnostic_triage") or "").strip()
    ac = (obj.get("actions") or "").strip()
    return dt, ac

def clamp(s: str, max_chars: int) -> str:
    s = (s or "").strip()
    if len(s) <= max_chars:
        return s
    return s[:max_chars].rstrip() + "…"
