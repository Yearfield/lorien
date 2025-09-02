"""
Outcomes router for PUT /outcomes/{node_id} endpoint.

Delegates to triage upsert with Pydantic validation and leaf-only guardrails.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator
from core.text_utils import enforce_phrase_rules
from storage.sqlite import SQLiteRepository
from api.dependencies import get_repository

router = APIRouter(prefix="/outcomes", tags=["outcomes"])

# Constants from triage router
TRIAGE_MAX_WORDS = 7
ACTIONS_MAX_WORDS = 7


class OutcomesUpdate(BaseModel):
    """Request model for updating outcomes (triage)."""
    diagnostic_triage: str = ""
    actions: str = ""

    @field_validator("diagnostic_triage")
    @classmethod
    def _v_triage(cls, v: str) -> str:
        if v is None:
            return ""
        return enforce_phrase_rules(v, TRIAGE_MAX_WORDS)

    @field_validator("actions")
    @classmethod
    def _v_actions(cls, v: str) -> str:
        if v is None:
            return ""
        return enforce_phrase_rules(v, ACTIONS_MAX_WORDS)


@router.put("/{node_id}")
async def put_outcomes(
    node_id: int,
    payload: OutcomesUpdate,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Update outcomes (triage) for a node (leaf-only).

    Delegates to triage upsert with Pydantic validation and guardrails.
    """
    # Validate node is a leaf (same as triage endpoint)
    node = repo.get_node(node_id)
    if not node or not node.is_leaf:
        raise HTTPException(
            status_code=422,
            detail="Triage can only be updated for leaf nodes"
        )

    # Pydantic validators handle word caps, regex, and phrase rules
    # If validation fails, FastAPI returns 422 with Pydantic detail array

    # Delegate to triage upsert (same logic as triage endpoint)
    success = repo.update_triage(node_id, payload.diagnostic_triage, payload.actions)
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Failed to update outcomes"
        )

    return {
        "node_id": node_id,
        "diagnostic_triage": payload.diagnostic_triage,
        "actions": payload.actions,
        "is_leaf": True
    }
