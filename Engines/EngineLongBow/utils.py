import unicodedata

def norm(s: str) -> str:
    """Normalize string for grouping/lookup (NFKC + casefold + whitespace collapse)"""
    if not s:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = " ".join(s.strip().split())
    return s.casefold()
