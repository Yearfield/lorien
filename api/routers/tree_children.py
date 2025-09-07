"""
Tree children router for bulk upsert operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field, field_validator
from typing import List
from ..dependencies import get_db_connection

router = APIRouter(prefix="/tree", tags=["tree-children"])

class SlotUpdate(BaseModel):
    slot: int = Field(..., ge=1, le=5)
    label: str  # "" means ignore/unchanged in Phase-6

    @field_validator("label")
    @classmethod
    def v_label(cls, v: str):
        # Allow empty to mean "ignore" for Phase-6 (no deletes), else enforce non-empty printable
        if v == "":
            return v
        txt = v.strip()
        if not txt:
            raise ValueError("label cannot be empty")
        # Simple allowlist mirroring Outcomes (letters/digits/space/comma/hyphen)
        import re
        if not re.fullmatch(r"[A-Za-z0-9 ,\-]+", txt):
            raise ValueError("label must be alnum/comma/hyphen/space")
        return txt

class ChildUpdate(BaseModel):
    slot: int = Field(..., ge=1, le=5)
    label: str = Field(..., min_length=1)

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str):
        """Validate label format (alnum/comma/hyphen/space only)."""
        import re
        if not re.fullmatch(r"[A-Za-z0-9 ,\-]+", v.strip()):
            raise ValueError("label must be alnum/comma/hyphen/space")
        return v.strip()


class BulkChildrenRequest(BaseModel):
    children: List[ChildUpdate] = Field(..., max_items=5)


class BulkChildrenResponse(BaseModel):
    updated: List[dict]
    missing_slots: str  # e.g., "2,4"


@router.post("/{parent_id:int}/children", response_model=BulkChildrenResponse)
def bulk_update_children(
    parent_id: int = Path(..., ge=1),
    request: BulkChildrenRequest = ...,
    conn = Depends(get_db_connection)
):
    """
    Atomic bulk update of children slots (1-5) for a parent node.

    All children in request are updated/created atomically.
    Returns updated children and remaining missing slots.
    Returns 422 with field-level errors on validation failures.
    Returns 409 if slot conflicts detected.
    """
    cursor = conn.cursor()

    # Validate parent exists and get its depth
    cursor.execute("SELECT depth FROM nodes WHERE id = ?", (parent_id,))
    parent_row = cursor.fetchone()
    if not parent_row:
        raise HTTPException(status_code=404, detail=f"Parent {parent_id} not found")

    parent_depth = parent_row[0]
    if parent_depth >= 5:
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["path", "parent_id"],
                "msg": "Cannot add children to leaf node",
                "type": "value_error.leaf_parent"
            }
        ])

    child_depth = parent_depth + 1

    # Validate no duplicate slots in request
    seen_slots = set()
    for i, child in enumerate(request.children):
        if child.slot in seen_slots:
            raise HTTPException(status_code=422, detail=[
                {
                    "loc": ["body", "children", i, "slot"],
                    "msg": "Duplicate slot in request",
                    "type": "value_error.duplicate_slot"
                }
            ])
        seen_slots.add(child.slot)

    # Start transaction
    conn.execute("BEGIN IMMEDIATE TRANSACTION")

    try:
        updated = []

        for i, child in enumerate(request.children):
            try:
                # Check if child already exists
                cursor.execute("""
                    SELECT id, label FROM nodes
                    WHERE parent_id = ? AND slot = ?
                """, (parent_id, child.slot))

                existing = cursor.fetchone()

                if existing:
                    # Update existing child
                    cursor.execute("""
                        UPDATE nodes
                        SET label = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
                        WHERE id = ?
                    """, (child.label, existing[0]))
                    child_id = existing[0]
                else:
                    # Insert new child
                    cursor.execute("""
                        INSERT INTO nodes (parent_id, depth, slot, label)
                        VALUES (?, ?, ?, ?)
                    """, (parent_id, child_depth, child.slot, child.label))
                    child_id = cursor.lastrowid

                updated.append({
                    "id": child_id,
                    "slot": child.slot,
                    "label": child.label
                })

            except Exception as e:
                raise HTTPException(status_code=422, detail=[
                    {
                        "loc": ["body", "children", i, "label"],
                        "msg": str(e),
                        "type": "value_error.label_invalid"
                    }
                ])

        # Recompute missing slots
        cursor.execute("""
            WITH slots(slot) AS (VALUES (1),(2),(3),(4),(5))
            SELECT GROUP_CONCAT(s.slot)
            FROM slots s
            LEFT JOIN nodes c ON c.parent_id = ? AND c.slot = s.slot
            WHERE c.id IS NULL
        """, (parent_id,))

        missing_row = cursor.fetchone()
        missing_slots = missing_row[0] if missing_row[0] else ""

        conn.commit()

        return BulkChildrenResponse(
            updated=updated,
            missing_slots=missing_slots
        )

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=422, detail=[
            {
                "loc": ["body"],
                "msg": str(e),
                "type": "value_error.bulk_update"
            }
        ])
