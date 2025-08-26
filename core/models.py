"""
Core domain models for decision tree entities.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class NodeType(str, Enum):
    """Types of nodes in the decision tree."""
    ROOT = "root"
    INTERNAL = "internal"
    LEAF = "leaf"


class Node(BaseModel):
    """Represents a node in the decision tree."""
    id: Optional[int] = None
    parent_id: Optional[int] = None
    depth: int = Field(..., ge=0, le=5)  # 0 = Root (Vital Measurement), 1-5 = Node 1-5
    slot: int = Field(..., ge=0, le=5)   # 0 = root, 1-5 = child position
    label: str = Field(..., min_length=1)
    is_leaf: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @field_validator('is_leaf')
    @classmethod
    def set_is_leaf(cls, v, info):
        """Automatically set is_leaf based on depth."""
        if 'depth' in info.data:
            return info.data['depth'] == 5
        return v

    @field_validator('slot')
    @classmethod
    def validate_slot(cls, v, info):
        """Validate slot based on depth."""
        if 'depth' in info.data:
            if info.data['depth'] == 0 and v != 0:
                raise ValueError("Root node must have slot 0")
            if info.data['depth'] >= 1 and (v < 1 or v > 5):
                raise ValueError("Child nodes must have slot 1-5")
        return v


class Parent(BaseModel):
    """Represents a parent node with its children."""
    node: Node
    children: List[Node] = Field(default_factory=list)
    
    @field_validator('children')
    @classmethod
    def validate_children_count(cls, v):
        """Ensure exactly 5 children."""
        if len(v) != 5:
            raise ValueError(f"Parent must have exactly 5 children, got {len(v)}")
        return v


class Path(BaseModel):
    """Represents a complete path through the decision tree."""
    nodes: List[Node] = Field(..., min_length=1, max_length=6)
    
    @field_validator('nodes')
    @classmethod
    def validate_path_structure(cls, v):
        """Validate path structure."""
        if not v:
            raise ValueError("Path cannot be empty")
        
        # Check depth progression
        for i, node in enumerate(v):
            if node.depth != i:
                raise ValueError(f"Node at position {i} has depth {node.depth}, expected {i}")
        
        return v


class RedFlag(BaseModel):
    """Represents a red flag that can be assigned to nodes."""
    id: Optional[int] = None
    name: str = Field(..., min_length=1)
    description: Optional[str] = None
    severity: str = Field(default="medium")  # low, medium, high, critical
    created_at: datetime = Field(default_factory=datetime.now)


class Triaging(BaseModel):
    """Represents diagnostic triage and actions for a node."""
    node_id: int
    diagnostic_triage: str = Field(..., min_length=1)
    actions: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class TreeValidationResult(BaseModel):
    """Result of tree validation."""
    is_valid: bool
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def violation_count(self) -> int:
        return len(self.violations)


class ImportResult(BaseModel):
    """Result of importing data from external sources."""
    success: bool
    rows_imported: int = 0
    rows_skipped: int = 0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class ExportResult(BaseModel):
    """Result of exporting data to external formats."""
    success: bool
    rows_exported: int = 0
    format: str = "csv"
    filename: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
