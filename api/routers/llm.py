from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, conint, Field, model_validator
from typing import List, Literal, Optional
import sqlite3
import os
import logging

from core.llm.service import LLMService
from core.validation.outcomes import trim_words, validate_phrase
from core.services.triage_service import upsert_triage
from api.dependencies import get_db_connection

router = APIRouter(prefix="/llm", tags=["LLM"])
logger = logging.getLogger(__name__)

class FillRequest(BaseModel):
    root: str = Field(..., min_length=1)
    nodes: List[str] = Field(default_factory=list, max_length=5)  # Node 1..5 in order; missing allowed
    triage_style: Literal["diagnosis-only","short-explanation","none"] = "diagnosis-only"
    actions_style: Literal["referral-only","steps","none"] = "referral-only"
    apply: bool = False      # write to DB if true
    node_id: Optional[conint(ge=1)] = None  # required if apply=true

    @model_validator(mode='after')
    def validate_node_id_when_apply(self):
        if self.apply and self.node_id is None:
            raise ValueError("node_id is required when apply=true")
        return self

class FillResponse(BaseModel):
    diagnostic_triage: str
    actions: str
    applied: bool = False

@router.get("/health")
async def llm_health():
    """
    LLM health check endpoint.

    Returns:
        JSONResponse with status code 200/503/500 and top-level JSON body
    """
    try:
        from datetime import datetime, timezone
        service = LLMService()
        status_code, body = service.health()
        body["checked_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        return JSONResponse(status_code=status_code, content=body)
    except Exception as e:
        logger.exception("Unexpected error in LLM health endpoint")
        from datetime import datetime, timezone
        return JSONResponse(
            status_code=500,
            content={
                "ok": False,
                "error": "internal",
                "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
            }
        )

@router.post("/fill-triage-actions", response_model=FillResponse)
def llm_fill(req: FillRequest, conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Generate diagnostic triage and actions using local LLM.

    Preserves existing contract: 7-word caps, regex, banned dosing tokens.
    Returns 422 on non-leaf apply=true with suggestions.
    Returns 503 when health unusable.

    Args:
        req: Request with root, nodes, styles, and optional apply settings
        conn: Database connection

    Returns:
        FillResponse with generated content and application status
    """
    # Check LLM health first
    svc = LLMService()
    if not svc.enabled:
        return JSONResponse(status_code=503, content={"ok": False, "ready": False})

    # Generate suggestions
    try:
        # Mock response for now
        raw_dt = f"Based on the path {req.root} -> {' -> '.join(req.nodes)}, consider {req.triage_style} assessment."
        raw_ac = f"Recommended {req.actions_style} actions for this clinical scenario."
    except Exception as e:
        logger.exception("Error generating LLM suggestions")
        raise HTTPException(status_code=500, detail="Failed to generate suggestions")

    # Clamp and validate
    dt = trim_words(raw_dt)
    ac = trim_words(raw_ac)
    validate_phrase("diagnostic_triage", dt)
    validate_phrase("actions", ac)

    applied = False
    if req.apply:

        # Check if node is a leaf (existing contract)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT is_leaf FROM nodes WHERE id = ?", (req.node_id,))
            row = cursor.fetchone()
            if not row or not row[0]:
                # Non-leaf apply - return 422 with suggestions
                return JSONResponse(status_code=422, content={
                    "error": "Cannot apply triage/actions to non-leaf node",
                    "diagnostic_triage": dt,
                    "actions": ac
                })
        except HTTPException:
            raise
        except Exception as e:
            logger.exception("Error checking node type")
            raise HTTPException(status_code=500, detail="Database error")

        # Apply to database
        try:
            upsert_triage(conn, int(req.node_id), dt, ac)
            applied = True
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # Return as dict to ensure all fields are included
    return {
        "diagnostic_triage": dt,
        "actions": ac,
        "applied": applied
    }
