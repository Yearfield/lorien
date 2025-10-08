from collections.abc import Iterable
from typing import Any

from fastapi import HTTPException, status


def _norm_label(s: str) -> str:
    return (s or "").strip()


def validate_child_labels_and_limit(children: Iterable[Any], limit: int = 5) -> list[str]:
    """
    Normalize and validate incoming children.
    - trims labels
    - rejects duplicates (case-insensitive)
    - rejects more than `limit`
    Returns normalized label list in order.
    """
    labels = []
    for c in children:
        lab = _norm_label(getattr(c, "label", c.get("label") if isinstance(c, dict) else None))
        if lab:
            labels.append(lab)
    lower = [label.lower() for label in labels]
    if len(lower) != len(set(lower)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {"loc": ["children"], "msg": "duplicate labels", "type": "value_error.duplicate"}
            ],
        )
    if len(labels) > limit:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[
                {
                    "loc": ["children"],
                    "msg": f"too many children: {len(labels)}>{limit}",
                    "type": "value_error.max_children",
                }
            ],
        )
    return labels


def coerce_assigned_slots(labels: list[str]) -> list[dict[str, Any]]:
    """Map labels → sequential slots starting at 1."""
    return [{"label": lab, "slot": i + 1} for i, lab in enumerate(labels)]
