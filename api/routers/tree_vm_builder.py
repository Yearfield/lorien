"""
Tree VM Builder and Wizard router for creating new decision trees.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
import sqlite3
import logging
import uuid
from datetime import datetime, timezone

from ..dependencies import get_db_connection

router = APIRouter(prefix="/tree", tags=["tree-vm-builder"])
logger = logging.getLogger(__name__)


class CreateVMRequest(BaseModel):
    label: str = Field(..., min_length=1, max_length=100, description="Vital Measurement label")

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str):
        """Validate VM label format."""
        import re
        if not re.fullmatch(r"[A-Za-z0-9 ,\-]+", v.strip()):
            raise ValueError("label must be alnum/comma/hyphen/space")
        return v.strip()


class CreateVMResponse(BaseModel):
    root_id: int
    label: str
    children_created: int


class NodeDefinition(BaseModel):
    label: str = Field(..., min_length=1, max_length=100)
    children: Optional[List[str]] = Field(default_factory=list, max_items=5)

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str):
        """Validate node label format."""
        import re
        if not re.fullmatch(r"[A-Za-z0-9 ,\-]+", v.strip()):
            raise ValueError("label must be alnum/comma/hyphen/space")
        return v.strip()


class VMDefinition(BaseModel):
    label: str = Field(..., min_length=1, max_length=100)
    node1: Optional[List[str]] = Field(default_factory=list, max_items=5)
    node2: Optional[List[str]] = Field(default_factory=list, max_items=5)
    node3: Optional[List[str]] = Field(default_factory=list, max_items=5)
    node4: Optional[List[str]] = Field(default_factory=list, max_items=5)

    @field_validator("label")
    @classmethod
    def validate_label(cls, v: str):
        """Validate VM label format."""
        import re
        if not re.fullmatch(r"[A-Za-z0-9 ,\-]+", v.strip()):
            raise ValueError("label must be alnum/comma/hyphen/space")
        return v.strip()


class SheetWizardRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    vms: List[VMDefinition] = Field(..., min_items=1, max_items=100)


class SheetWizardResponse(BaseModel):
    staged_id: str
    name: str
    vm_count: int
    total_nodes: int


class SheetCommitRequest(BaseModel):
    staged_id: str
    enforce_five: bool = True
    prune_safe: bool = True


class SheetCommitResponse(BaseModel):
    committed: bool
    root_ids: List[int]
    report: Dict[str, Any]


# In-memory storage for staged sheets (in production, use database)
_staged_sheets = {}


@router.post("/roots", response_model=CreateVMResponse)
def create_vital_measurement(
    request: CreateVMRequest,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Create a new Vital Measurement (root node) with 5 empty children slots.

    Returns the root ID and confirmation of children creation.
    """
    cursor = conn.cursor()

    # Start transaction
    conn.execute("BEGIN IMMEDIATE TRANSACTION")

    try:
        # Check for duplicate VM labels
        cursor.execute("""
            SELECT id FROM nodes
            WHERE depth = 0 AND LOWER(label) = LOWER(?)
        """, (request.label,))

        if cursor.fetchone():
            raise HTTPException(status_code=422, detail=[
                {
                    "loc": ["body", "label"],
                    "msg": "Vital Measurement with this label already exists",
                    "type": "value_error.duplicate_vm"
                }
            ])

        # Create root node
        cursor.execute("""
            INSERT INTO nodes (parent_id, depth, slot, label)
            VALUES (NULL, 0, 0, ?)
        """, (request.label,))

        root_id = cursor.lastrowid

        # Create 5 empty children slots
        children_created = 0
        for slot in range(1, 6):
            placeholder_label = f"Slot {slot}"
            cursor.execute("""
                INSERT INTO nodes (parent_id, depth, slot, label)
                VALUES (?, 1, ?, ?)
            """, (root_id, slot, placeholder_label))
            children_created += 1

        conn.commit()

        return CreateVMResponse(
            root_id=root_id,
            label=request.label,
            children_created=children_created
        )

    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        logger.exception("Error creating VM")
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/wizard/sheet", response_model=SheetWizardResponse)
def stage_sheet_wizard(
    request: SheetWizardRequest,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Stage a complete sheet definition for later commit.

    Validates the structure and returns a staged ID for committing.
    """
    try:
        # Validate VM labels are unique
        vm_labels = set()
        total_nodes = 0

        for vm in request.vms:
            if vm.label.lower() in vm_labels:
                raise HTTPException(status_code=422, detail=[
                    {
                        "loc": ["body", "vms"],
                        "msg": f"Duplicate VM label: {vm.label}",
                        "type": "value_error.duplicate_vm_label"
                    }
                ])
            vm_labels.add(vm.label.lower())

            # Count nodes in this VM
            node_levels = [vm.node1 or [], vm.node2 or [], vm.node3 or [], vm.node4 or []]
            for level_nodes in node_levels:
                total_nodes += len(level_nodes)

        # Check for existing VMs with same labels
        cursor = conn.cursor()
        for vm_label in vm_labels:
            cursor.execute("""
                SELECT id FROM nodes
                WHERE depth = 0 AND LOWER(label) = LOWER(?)
            """, (vm_label,))

            if cursor.fetchone():
                raise HTTPException(status_code=422, detail=[
                    {
                        "loc": ["body", "vms"],
                        "msg": f"VM label already exists: {vm_label}",
                        "type": "value_error.existing_vm_label"
                    }
                ])

        # Stage the sheet definition
        staged_id = str(uuid.uuid4())
        _staged_sheets[staged_id] = {
            "name": request.name,
            "vms": request.vms,
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

        return SheetWizardResponse(
            staged_id=staged_id,
            name=request.name,
            vm_count=len(request.vms),
            total_nodes=total_nodes
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error staging sheet wizard")
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/wizard/sheet/commit", response_model=SheetCommitResponse)
def commit_sheet_wizard(
    request: SheetCommitRequest,
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    """
    Commit a staged sheet definition to create the actual tree structure.

    Runs materialization to ensure 5-children invariant.
    """
    try:
        # Get staged sheet
        if request.staged_id not in _staged_sheets:
            raise HTTPException(status_code=404, detail="Staged sheet not found")

        staged_sheet = _staged_sheets[request.staged_id]
        cursor = conn.cursor()

        # Start transaction
        conn.execute("BEGIN IMMEDIATE TRANSACTION")

        try:
            root_ids = []
            total_added = 0
            total_filled = 0

            # Create each VM and its tree structure
            for vm_def in staged_sheet["vms"]:
                # Create root
                cursor.execute("""
                    INSERT INTO nodes (parent_id, depth, slot, label)
                    VALUES (NULL, 0, 0, ?)
                """, (vm_def.label,))

                root_id = cursor.lastrowid
                root_ids.append(root_id)

                # Create node levels
                node_levels = [
                    (vm_def.node1 or [], 1),
                    (vm_def.node2 or [], 2),
                    (vm_def.node3 or [], 3),
                    (vm_def.node4 or [], 4)
                ]

                parent_ids_by_level = {0: root_id}  # level -> parent_id mapping

                for level_nodes, depth in node_levels:
                    if not level_nodes:
                        continue

                    # Create nodes for this level
                    for slot, node_label in enumerate(level_nodes, 1):
                        parent_id = parent_ids_by_level.get(depth - 1)
                        if not parent_id:
                            continue

                        cursor.execute("""
                            INSERT INTO nodes (parent_id, depth, slot, label)
                            VALUES (?, ?, ?, ?)
                        """, (parent_id, depth, slot, node_label))

                        node_id = cursor.lastrowid
                        parent_ids_by_level[depth] = node_id
                        total_added += 1

            # Run materialization to ensure 5-children invariant
            from .tree_materialize import _perform_materialization
            from .tree_materialize import MaterializeReport

            # Get all newly created parents that need materialization
            cursor.execute("""
                SELECT id, label, depth FROM nodes
                WHERE depth BETWEEN 0 AND 4 AND id IN ({})
            """.format(",".join("?" * len(root_ids))), root_ids)

            target_parents = cursor.fetchall()
            materialize_report = _perform_materialization(cursor, target_parents, request)

            conn.commit()

            # Clean up staged sheet
            del _staged_sheets[request.staged_id]

            return SheetCommitResponse(
                committed=True,
                root_ids=root_ids,
                report={
                    "added": total_added + materialize_report.added,
                    "filled": total_filled + materialize_report.filled,
                    "pruned": materialize_report.pruned,
                    "kept": materialize_report.kept,
                    "vms_created": len(root_ids)
                }
            )

        except Exception as e:
            conn.rollback()
            logger.exception("Error committing sheet wizard")
            raise HTTPException(status_code=422, detail=[
                {
                    "loc": ["body", "staged_id"],
                    "msg": f"Failed to commit sheet: {str(e)}",
                    "type": "value_error.commit_failed"
                }
            ])

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in sheet commit")
        raise HTTPException(status_code=500, detail="Database error")


