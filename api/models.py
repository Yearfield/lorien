"""Pydantic models for API request/response DTOs."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# Constants imported from core.constants if needed


class IncompleteParentDTO(BaseModel):
    parent_id: int = Field(..., description="Parent node ID")
    missing_slots: List[int] = Field(..., description="List of missing slot numbers (1-5)")


class DBInfo(BaseModel):
    wal: bool = Field(..., description="Whether WAL mode is enabled")
    foreign_keys: bool = Field(..., description="Whether foreign keys are enabled")
    page_size: int = Field(..., description="Database page size")
    path: str = Field(..., description="Database file path")


class HealthResponse(BaseModel):
    ok: bool = Field(..., description="Overall health status")
    version: str = Field(..., description="API version")
    db: DBInfo = Field(..., description="Database information")
    features: Dict[str, bool] = Field(..., description="Feature flags")
    metrics: Optional[Dict[str, Any]] = Field(default=None, description="Optional runtime metrics when analytics enabled")
    
    class Config:
        exclude_none = True


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
    code: Optional[str] = Field(None, description="Error code")
