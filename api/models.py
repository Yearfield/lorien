"""
Pydantic models for API request/response DTOs.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, conint, constr, conlist

from core.constants import APP_VERSION, APP_NAME


class ChildSlot(BaseModel):
    """Represents a single child slot in a parent node."""
    slot: conint(ge=1, le=5) = Field(..., description="Slot number (1-5)")
    label: constr(min_length=1) = Field(..., description="Node label")


class ChildrenUpsert(BaseModel):
    """Request model for upserting multiple children at once."""
    children: conlist(ChildSlot, min_length=1, max_length=5) = Field(
        ..., description="List of children to upsert (1-5 items)"
    )


class TriageDTO(BaseModel):
    """Request/response model for triage data."""
    diagnostic_triage: Optional[str] = Field(None, description="Diagnostic triage text")
    actions: Optional[str] = Field(None, description="Actions to take")


class IncompleteParentDTO(BaseModel):
    """Response model for incomplete parent information."""
    parent_id: int = Field(..., description="Parent node ID")
    missing_slots: List[int] = Field(..., description="List of missing slot numbers (1-5)")


class RedFlagAssignment(BaseModel):
    """Request model for assigning red flags to nodes."""
    node_id: int = Field(..., description="Node ID to assign flag to")
    red_flag_name: str = Field(..., min_length=1, description="Name of red flag to assign")


class HealthResponse(BaseModel):
    """Health check response."""
    ok: bool = True
    version: str = APP_VERSION
    db: Dict[str, Any] = Field(..., description="Database information")
    features: Dict[str, bool] = Field(..., description="Feature flags")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    code: Optional[str] = Field(None, description="Error code")
