"""
Unified importer router for POST /import endpoint.

Delegates to existing import logic with strict 422 ctx for schema errors.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
import io
from datetime import datetime
from typing import Dict, Any
import logging

from ..dependencies import get_repository, get_db_connection
from storage.sqlite import SQLiteRepository
from core.import_export import assert_csv_header
import sqlite3

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/import", tags=["import"])


def _persist_import_data(df: pd.DataFrame, repo: SQLiteRepository) -> Dict[str, Any]:
    """
    Persist import data to database in a single transaction.
    
    Args:
        df: Validated DataFrame with 8 columns
        repo: SQLite repository instance
        
    Returns:
        Dict with import results
    """
    with repo._get_connection() as conn:
        cursor = conn.cursor()
        
        created_roots = 0
        created_nodes = 0
        updated_nodes = 0
        updated_outcomes = 0
        
        for index, row in df.iterrows():
            # Get row data
            vm_label = str(row["Vital Measurement"]).strip()
            node_labels = [str(row[f"Node {i}"]).strip() for i in range(1, 6)]
            diagnosis = str(row["Diagnostic Triage"]).strip() if pd.notna(row["Diagnostic Triage"]) else ""
            actions = str(row["Actions"]).strip() if pd.notna(row["Actions"]) else ""
            
            # Skip empty rows
            if not vm_label or vm_label.lower() in ['', 'nan', 'none']:
                continue
            
            # 1. Upsert root VM by label (depth=0)
            cursor.execute("""
                SELECT id FROM nodes 
                WHERE depth = 0 AND LOWER(label) = LOWER(?)
            """, (vm_label,))
            
            root_result = cursor.fetchone()
            if root_result:
                root_id = root_result[0]
            else:
                cursor.execute("""
                    INSERT INTO nodes (parent_id, depth, slot, label, is_leaf)
                    VALUES (NULL, 0, 0, ?, 0)
                """, (vm_label,))
                root_id = cursor.lastrowid
                created_roots += 1
            
            # 2. For Node 1..5: create/upsert under correct parent with slots 1..5
            for slot, node_label in enumerate(node_labels, 1):
                if not node_label or node_label.lower() in ['', 'nan', 'none']:
                    continue
                
                # Check if node already exists at this slot
                cursor.execute("""
                    SELECT id FROM nodes 
                    WHERE parent_id = ? AND slot = ?
                """, (root_id, slot))
                
                node_result = cursor.fetchone()
                if node_result:
                    # Update existing node
                    cursor.execute("""
                        UPDATE nodes SET label = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (node_label, node_result[0]))
                    updated_nodes += 1
                else:
                    # Create new node
                    cursor.execute("""
                        INSERT INTO nodes (parent_id, depth, slot, label, is_leaf)
                        VALUES (?, 1, ?, ?, 0)
                    """, (root_id, slot, node_label))
                    created_nodes += 1
            
            # 3. For the leaf: upsert triage/actions
            # Find the leaf node (depth 5) or create a path to it
            leaf_id = _ensure_leaf_path(cursor, root_id, node_labels)
            
            if leaf_id and (diagnosis or actions):
                # Upsert triage data
                cursor.execute("""
                    INSERT OR REPLACE INTO triage (node_id, diagnostic_triage, actions, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                """, (leaf_id, diagnosis, actions))
                updated_outcomes += 1
        
        return {
            "status": "success",
            "rows_processed": len(df),
            "created": {
                "roots": created_roots,
                "nodes": created_nodes
            },
            "updated": {
                "nodes": updated_nodes,
                "outcomes": updated_outcomes
            }
        }


def _ensure_leaf_path(cursor: sqlite3.Cursor, root_id: int, node_labels: list) -> int:
    """
    Ensure a complete path exists from root to leaf (depth 5).
    Returns the leaf node ID.
    """
    current_id = root_id
    current_depth = 0
    
    for slot, node_label in enumerate(node_labels, 1):
        if not node_label or node_label.lower() in ['', 'nan', 'none']:
            # Create placeholder node
            node_label = f"Slot {slot}"
        
        current_depth += 1
        
        # Check if child exists at this depth
        cursor.execute("""
            SELECT id FROM nodes 
            WHERE parent_id = ? AND depth = ? AND slot = ?
        """, (current_id, current_depth, slot))
        
        child_result = cursor.fetchone()
        if child_result:
            current_id = child_result[0]
        else:
            # Create child node
            is_leaf = 1 if current_depth == 5 else 0
            cursor.execute("""
                INSERT INTO nodes (parent_id, depth, slot, label, is_leaf)
                VALUES (?, ?, ?, ?, ?)
            """, (current_id, current_depth, slot, node_label, is_leaf))
            current_id = cursor.lastrowid
    
    return current_id


def _process_import(content: bytes, filename: str, repo: SQLiteRepository) -> Dict[str, Any]:
    """
    Process import file with strict validation.

    Args:
        content: File content as bytes
        filename: Original filename

    Returns:
        Dict with import results

    Raises:
        HTTPException: With 422 ctx on schema errors
    """
    try:
        # Parse Excel file
        df = pd.read_excel(io.BytesIO(content))

        # Validate headers with strict ctx
        headers = df.columns.tolist()
        try:
            assert_csv_header(headers)
            logger.info("Headers validated successfully")
        except ValueError as e:
            # Extract ctx from ValueError
            error_ctx = e.args[0] if isinstance(e.args[0], dict) else {
                "first_offending_row": 0,
                "col_index": 0,
                "expected": ["Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5", "Diagnostic Triage", "Actions"],
                "received": headers,
                "error_counts": {"header": 1}
            }

            # Build FastAPI 422 detail with ctx for first mismatch & counts
            detail = [{
                "loc": ["body", "file"],
                "msg": "CSV header mismatch",
                "type": "value_error.csv_schema",
                "ctx": error_ctx
            }]

            raise HTTPException(
                status_code=422,
                detail=detail
            )

        # Process the validated data and persist to database
        return _persist_import_data(df, repo)

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Import processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Import processing failed: {str(e)}"
        )


@router.post("")
async def import_workbook(
    file: UploadFile = File(...),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Unified importer for POST /import endpoint.

    Strict 422 ctx for schema errors with detailed mismatch information.
    """
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx files are supported"
        )

    try:
        # Read file content
        content = await file.read()

        # Process import with strict validation
        result = _process_import(content, file.filename, repo)

        return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during import: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Import failed: {str(e)}"
        )
