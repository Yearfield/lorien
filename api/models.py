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
    children: conlist(ChildSlot, min_length=5, max_length=5) = Field(
        ..., description="List of children to upsert (exactly 5 items required)"
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
    user: Optional[str] = Field(None, description="User performing the assignment (for audit)")
    cascade: bool = Field(False, description="Whether to apply to parent + all descendants")


class DBInfo(BaseModel):
    """Database information for health checks."""
    wal: bool = Field(..., description="Whether WAL mode is enabled")
    foreign_keys: bool = Field(..., description="Whether foreign keys are enabled")
    page_size: int = Field(..., description="Database page size")
    path: str = Field(..., description="Database file path")


class HealthResponse(BaseModel):
    """Health check response."""
    ok: bool = Field(..., description="Overall health status")
    version: str = Field(..., description="API version")
    db: DBInfo = Field(..., description="Database information")
    features: Dict[str, bool] = Field(..., description="Feature flags")


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    code: Optional[str] = Field(None, description="Error code")
