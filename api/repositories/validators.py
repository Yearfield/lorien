from typing import Iterable

def ensure_unique_5(labels: Iterable[str]) -> list[str]:
    clean = [x.strip() for x in labels if x and str(x).strip()]
    if len(clean) != len(set(clean)):
        raise ValueError("duplicate_labels")
    if len(clean) != 5:
        raise ValueError("must_choose_five")
    return clean
