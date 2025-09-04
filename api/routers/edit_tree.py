"""
Edit Tree router for parent children management with optimistic concurrency.
"""

from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel, Field, conint, constr
from typing import List
from typing import List, Optional
import logging

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from core.services.tree_service import (
    parse_if_match, children_read, children_snapshot,
    validate_five_slots, validate_duplicate_labels,
    build_slot_conflicts, children_update_apply
)

router = APIRouter(prefix="/tree", tags=["Tree"])
logger = logging.getLogger(__name__)


class ChildView(BaseModel):
    slot: conint(ge=1, le=5)
    node_id: int
    label: constr(pattern=r"^[A-Za-z0-9 ,\-]*$", strip_whitespace=True)
    updated_at: str


class PathView(BaseModel):
    node_id: int
    is_leaf: bool
    depth: int
    vital_measurement: str
    nodes: List[str]  # Always length 5, padded with ""


class ChildrenReadOut(BaseModel):
    parent_id: int
    version: int
    missing_slots: List[int]
    children: List[ChildView]  # Always exactly 5 items
    path: PathView
    etag: str


class ChildSlot(BaseModel):
    slot: conint(ge=1, le=5)
    label: constr(pattern=r"^[A-Za-z0-9 ,\-]*$", strip_whitespace=True)


class ChildrenUpdateIn(BaseModel):
    version: Optional[int] = None
    children: List[ChildSlot]  # Must contain exactly 5 items


class ChildrenUpdateOut(BaseModel):
    parent_id: int
    version: int
    missing_slots: List[int]
    updated: List[int]


@router.get("/parent/{parent_id}/children", response_model=ChildrenReadOut)
def read_parent_children(parent_id: int, repo: SQLiteRepository = Depends(get_repository)):
    """
    Read all 5 children of a parent node with optimistic concurrency metadata.

    Returns 5 child slots (creating missing ones), version, missing_slots,
    path context, and ETag for optimistic concurrency.

    Args:
        parent_id: Parent node ID
        repo: Database repository

    Returns:
        ChildrenReadOut with full context

    Raises:
        404: Parent not found
    """
    result = children_read(repo, parent_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Parent not found")

    return result


@router.put("/parent/{parent_id}/children", response_model=ChildrenUpdateOut)
def update_parent_children(
    parent_id: int,
    body: ChildrenUpdateIn,
    if_match: Optional[str] = Header(default=None, alias="If-Match"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Update parent children with optimistic concurrency control.

    Args:
        parent_id: Parent node ID
        body: Update request with version and children
        if_match: If-Match header for optimistic concurrency
        repo: Database repository

    Returns:
        ChildrenUpdateOut with updated slots and new version

    Raises:
        400: Version mismatch between header and body
        404: Parent not found
        409: Conflict (stale version) with per-slot details
        422: Validation errors (missing slots, duplicates, etc.)
    """
    # 1) Resolve client version from If-Match or body
    client_version = parse_if_match(if_match) if if_match else body.version

    if if_match and body.version is not None and client_version != body.version:
        raise HTTPException(
            status_code=400,
            detail=[{
                "loc": ["header", "If-Match"],
                "msg": "Version mismatch between header and body",
                "type": "value_error.version_mismatch"
            }]
        )

    # 2) Validate exactly 5 slots
    try:
        validate_five_slots(body.children)
    except ValueError as e:
        missing_slots = e.args[0].get("missing_slots", [])
        raise HTTPException(
            status_code=422,
            detail=[{
                "loc": ["body", "children"],
                "msg": "Exactly 5 children required",
                "type": "value_error.children_count",
                "ctx": {"missing_slots": missing_slots}
            }]
        )

    # 3) Get current snapshot for validation
    current = children_snapshot(repo, parent_id)
    if current is None:
        raise HTTPException(status_code=404, detail="Parent not found")

    # 4) Check optimistic concurrency
    if client_version is not None and client_version != current["version"]:
        conflicts = build_slot_conflicts(body.children, current)
        if conflicts:
            # Add client version to each conflict
            for conflict in conflicts:
                conflict["ctx"]["client_version"] = client_version

            raise HTTPException(status_code=409, detail=conflicts)

    # 5) Validate duplicate labels
    duplicate_errors = validate_duplicate_labels(repo, parent_id, body.children)
    if duplicate_errors:
        raise HTTPException(status_code=422, detail=duplicate_errors)

    # 6) Apply updates
    try:
        result = children_update_apply(repo, parent_id, body.children, current["version"])
        return result
    except Exception as e:
        logger.exception("Error updating parent children")
        raise HTTPException(status_code=500, detail="Database error")
