from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, conint, Field
from typing import List, Literal, Optional
import sqlite3

from llm.config import load_llm_config
from llm.runner import fill_triage_actions
from core.services.triage_service import upsert_triage
from api.dependencies import get_db_connection

router = APIRouter(prefix="/llm", tags=["llm"])

class FillRequest(BaseModel):
    root: str = Field(..., min_length=1)
    nodes: List[str] = Field(default_factory=list, max_items=5)  # Node 1..5 in order; missing allowed
    triage_style: Literal["diagnosis-only","short-explanation","none"] = "diagnosis-only"
    actions_style: Literal["referral-only","steps","none"] = "referral-only"
    apply: bool = False      # write to DB if true
    node_id: Optional[conint(ge=1)] = None  # required if apply=true

class FillResponse(BaseModel):
    diagnostic_triage: str
    actions: str
    applied: bool = False

@router.post("/fill-triage-actions", response_model=FillResponse)
def llm_fill(req: FillRequest, conn: sqlite3.Connection = Depends(get_db_connection)):
    """
    Generate diagnostic triage and actions using local LLM.
    
    Args:
        req: Request with root, nodes, styles, and optional apply settings
        conn: Database connection
        
    Returns:
        FillResponse with generated content and application status
    """
    cfg = load_llm_config()
    if not cfg.enabled:
        raise HTTPException(status_code=503, detail="LLM is disabled")
    
    # Generate
    dt, ac = fill_triage_actions(req.root, req.nodes, req.triage_style, req.actions_style)

    applied = False
    if req.apply:
        if not req.node_id:
            raise HTTPException(status_code=400, detail="node_id is required when apply=true")
        if not dt and not ac:
            raise HTTPException(status_code=400, detail="No content generated to apply")
        
        try:
            upsert_triage(conn, int(req.node_id), dt, ac)
            applied = True
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    return FillResponse(diagnostic_triage=dt, actions=ac, applied=applied)
