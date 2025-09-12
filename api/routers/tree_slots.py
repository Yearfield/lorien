"""
Tree slots router for individual slot upsert and delete operations.
"""

from fastapi import APIRouter, HTTPException, Path, Depends, Response
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import sqlite3
import logging
import time

from ..dependencies import get_db_connection

router = APIRouter(prefix="/tree", tags=["tree-slots"])
logger = logging.getLogger(__name__)


class SlotUpdateRequest(BaseModel):
    label: str = Field(..., min_length=1, description="Label for the slot")

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str):
        """Validate label format (alnum/comma/hyphen/space only)."""
        import re
        if not re.fullmatch(r"[A-Za-z0-9 ,\-]+", v.strip()):
            raise ValueError("label must be alnum/comma/hyphen/space")
        return v.strip()


class SlotResponse(BaseModel):
    child_id: int
    parent_id: int
    slot: int
    label: str
    depth: int


class SlotDeleteResponse(BaseModel):
    ok: bool = True


@router.put("/{parent_id:int}/slot/{slot:int}", response_model=SlotResponse)
def upsert_slot(
    parent_id: int = Path(..., ge=1, description="Parent node ID"),
    slot: int = Path(..., ge=1, le=5, description="Slot number (1-5)"),
    request: SlotUpdateRequest = ...,
    conn: sqlite3.Connection = Depends(get_db_connection),
    response: Response = None
):
    """
    Upsert a child node in a specific slot.

    Creates new child if slot is empty, updates existing if occupied.
    Returns 409 if concurrent modification detected.
    Performance target: <40ms.
    
    DEPRECATED: Use /api/v1/tree/parents/{parent_id}/children instead.
    """
    # Add deprecation headers for legacy route
    if response is not None:
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "v7.0"
    
    start_time = time.time()

    try:
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

        # Start transaction
        conn.execute("BEGIN IMMEDIATE TRANSACTION")

        try:
            # Check if slot is already occupied by another child
            cursor.execute("""
                SELECT id, label FROM nodes
                WHERE parent_id = ? AND slot = ?
            """, (parent_id, slot))

            existing_child = cursor.fetchone()

            if existing_child:
                # Update existing child
                child_id = existing_child[0]
                cursor.execute("""
                    UPDATE nodes
                    SET label = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
                    WHERE id = ?
                """, (request.label, child_id))
            else:
                # Create new child
                cursor.execute("""
                    INSERT INTO nodes (parent_id, depth, slot, label)
                    VALUES (?, ?, ?, ?)
                """, (parent_id, child_depth, slot, request.label))
                child_id = cursor.lastrowid

            conn.commit()

            # Performance check
            elapsed = time.time() - start_time
            if elapsed > 0.04:  # 40ms
                logger.warning(".3f")

            return SlotResponse(
                child_id=child_id,
                parent_id=parent_id,
                slot=slot,
                label=request.label,
                depth=child_depth
            )

        except sqlite3.IntegrityError as e:
            conn.rollback()
            if "UNIQUE constraint failed" in str(e):
                # Slot uniqueness constraint violated
                raise HTTPException(status_code=409, detail=[
                    {
                        "loc": ["path", "slot"],
                        "msg": "Slot already occupied",
                        "type": "value_error.slot_conflict"
                    }
                ])
            else:
                raise HTTPException(status_code=422, detail=[
                    {
                        "loc": ["body", "label"],
                        "msg": "Label validation failed",
                        "type": "value_error.label_invalid"
                    }
                ])

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error upserting slot")
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/{parent_id:int}/slot/{slot:int}", response_model=SlotDeleteResponse)
def delete_slot(
    parent_id: int = Path(..., ge=1, description="Parent node ID"),
    slot: int = Path(..., ge=1, le=5, description="Slot number (1-5)"),
    conn: sqlite3.Connection = Depends(get_db_connection),
    response: Response = None
):
    """
    Delete a child node from a specific slot.

    Frees the slot for future use. Safe to call on empty slots.
    
    DEPRECATED: Use /api/v1/tree/parents/{parent_id}/children instead.
    """
    # Add deprecation headers for legacy route
    if response is not None:
        response.headers["Deprecation"] = "true"
        response.headers["Sunset"] = "v7.0"
    
    try:
        cursor = conn.cursor()

        # Validate parent exists
        cursor.execute("SELECT id FROM nodes WHERE id = ?", (parent_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail=f"Parent {parent_id} not found")

        # Delete child if it exists (safe operation)
        cursor.execute("""
            DELETE FROM nodes
            WHERE parent_id = ? AND slot = ?
        """, (parent_id, slot))

        return SlotDeleteResponse(ok=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error deleting slot")
        raise HTTPException(status_code=500, detail="Database error")


