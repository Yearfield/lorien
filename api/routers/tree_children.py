"""
Tree children router for bulk upsert operations.
"""

from fastapi import APIRouter, HTTPException, Path
from pydantic import BaseModel, Field, field_validator
from typing import List
from ..dependencies import get_db_connection

router = APIRouter(prefix="/tree/parents", tags=["tree-children"])

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

class BulkUpsertBody(BaseModel):
    slots: List[SlotUpdate]
    mode: str = "upsert"

@router.put("/{parent_id}/children")
def bulk_upsert_children(parent_id: int = Path(..., ge=1), body: BulkUpsertBody = ...):
    """
    Atomic bulk upsert of children slots (1-5) for a parent node.

    Only provided slots are updated; empty label="" means ignore.
    Returns updated children and remaining missing slots.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Validate parent exists and get its depth
    cursor.execute("SELECT depth FROM nodes WHERE id = ?", (parent_id,))
    parent_row = cursor.fetchone()
    if not parent_row:
        raise HTTPException(status_code=404, detail="parent not found")

    parent_depth = parent_row[0]
    if parent_depth >= 5:
        raise HTTPException(status_code=400, detail="cannot add children to leaf node")

    # Start transaction
    conn.execute("BEGIN IMMEDIATE TRANSACTION")

    try:
        updated = []

        for s in body.slots:
            if s.label == "":
                continue  # ignore (no delete this phase)

            # Calculate child depth and validate slot uniqueness
            child_depth = parent_depth + 1

            # Check if child already exists
            cursor.execute("""
                SELECT id, label FROM nodes
                WHERE parent_id = ? AND slot = ?
            """, (parent_id, s.slot))

            existing = cursor.fetchone()

            if existing:
                # Update existing child
                cursor.execute("""
                    UPDATE nodes
                    SET label = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
                    WHERE id = ?
                """, (s.label.strip(), existing[0]))
                child_id = existing[0]
            else:
                # Insert new child
                cursor.execute("""
                    INSERT INTO nodes (parent_id, depth, slot, label)
                    VALUES (?, ?, ?, ?)
                """, (parent_id, child_depth, s.slot, s.label.strip()))
                child_id = cursor.lastrowid

            updated.append({
                "id": child_id,
                "slot": s.slot,
                "label": s.label.strip()
            })

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

        return {
            "updated": updated,
            "missing_slots": missing_slots
        }

    except Exception as e:
        conn.rollback()
        # For Phase-6, treat most errors as validation errors
        raise HTTPException(status_code=422, detail=[{
            "loc": ["body", "slots"],
            "msg": str(e),
            "type": "value_error.upsert"
        }])
