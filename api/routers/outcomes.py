"""
Outcomes router for leaf-only triage and actions.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
import sqlite3
import logging

from ..dependencies import get_db_connection
from core.services.triage_service import upsert_triage
from core.validation.outcomes import trim_words, validate_phrase

router = APIRouter(prefix="/outcomes", tags=["outcomes"])
logger = logging.getLogger(__name__)


class OutcomesRequest(BaseModel):
    diagnostic_triage: str = Field(..., min_length=1)
    actions: str = Field(..., min_length=1)


class OutcomesResponse(BaseModel):
    diagnostic_triage: str
    actions: str
    applied: bool = True


@router.put("/{node_id}", response_model=OutcomesResponse)
def update_outcomes(
    node_id: int,
    request: OutcomesRequest,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Update diagnostic triage and actions for a leaf node.

    Validates content limits, regex, and prohibited tokens.
    Only allows updates to leaf nodes.

    Args:
        node_id: The node ID to update
        request: Outcomes data
        conn: Database connection

    Returns:
        OutcomesResponse with validated content

    Raises:
        422: Validation failed (word count, regex, prohibited tokens, empty)
        400: Database error or non-leaf node
    """
    # Normalize input
    dt_raw = request.diagnostic_triage.strip()
    ac_raw = request.actions.strip()

    # Reject empty after normalization
    if not dt_raw:
        raise HTTPException(
            status_code=422,
            detail=[{
                "loc": ["body", "diagnostic_triage"],
                "msg": "Diagnostic triage cannot be empty",
                "type": "value_error.empty"
            }]
        )

    if not ac_raw:
        raise HTTPException(
            status_code=422,
            detail=[{
                "loc": ["body", "actions"],
                "msg": "Actions cannot be empty",
                "type": "value_error.empty"
            }]
        )

    # Check if node is a leaf
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT is_leaf FROM nodes WHERE id = ?", (node_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Node not found")

        if not row[0]:
            raise HTTPException(
                status_code=400,
                detail="Cannot update outcomes for non-leaf node"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error checking node type")
        raise HTTPException(status_code=500, detail="Database error")

    # Validate and clamp content
    try:
        # Word cap ≤7 words per field
        dt = trim_words(dt_raw)
        ac = trim_words(ac_raw)

        # Whitelist regex ^[A-Za-z0-9 ,\-]+$
        validate_phrase("diagnostic_triage", dt)
        validate_phrase("actions", ac)

        # Prohibited dosing tokens (case-insensitive & pattern)
        # This is handled inside validate_phrase

    except ValueError as e:
        # Parse validation error
        error_msg = str(e)
        if "word count" in error_msg.lower():
            error_type = "value_error.word_count"
        elif "regex" in error_msg.lower():
            error_type = "value_error.regex"
        elif "dosing" in error_msg.lower() or "prohibited" in error_msg.lower():
            error_type = "value_error.prohibited_token"
        else:
            error_type = "value_error.validation"

        raise HTTPException(
            status_code=422,
            detail=[{
                "loc": ["body", "diagnostic_triage" if "diagnostic" in error_msg.lower() else "actions"],
                "msg": error_msg,
                "type": error_type
            }]
        )

    # Apply to database
    try:
        upsert_triage(conn, node_id, dt, ac)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return OutcomesResponse(
        diagnostic_triage=dt,
        actions=ac,
        applied=True
    )


# Legacy fallback endpoint
@router.put("/triage/{node_id}")
def update_triage_legacy(
    node_id: int,
    request: OutcomesRequest,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Legacy endpoint for updating triage (redirects to outcomes endpoint).

    DEPRECATED: Use PUT /outcomes/{node_id} instead.
    """
    # Reuse the same logic as the main outcomes endpoint
    return update_outcomes(node_id, request, conn)