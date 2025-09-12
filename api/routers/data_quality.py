"""
Data quality governance endpoints.

Provides endpoints for monitoring and repairing data quality issues
in the decision tree database.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any, List
import logging

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from ..repositories.validators import get_validation_rules

router = APIRouter(tags=["data-quality"])

@router.get("/admin/data-quality/summary")
async def get_data_quality_summary(repo: SQLiteRepository = Depends(get_repository)):
    """
    Get data quality summary with counts of various issues.
    
    Returns:
        200 with data quality metrics including:
        - slot_gaps: Parents with missing child slots
        - over_5_children: Parents with more than 5 children (should not happen)
        - orphans: Nodes without valid parent relationships
        - duplicate_paths: Duplicate node paths
        - validation_rules: Current validation rules
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # Count slot gaps (parents with missing child slots)
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT parent_id, COUNT(*) as child_count
                    FROM nodes 
                    WHERE parent_id IS NOT NULL
                    GROUP BY parent_id
                    HAVING child_count < 5
                ) as gaps
            """)
            slot_gaps = cursor.fetchone()[0]
            
            # Count parents with more than 5 children (should not happen)
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT parent_id, COUNT(*) as child_count
                    FROM nodes 
                    WHERE parent_id IS NOT NULL
                    GROUP BY parent_id
                    HAVING child_count > 5
                ) as over_5
            """)
            over_5_children = cursor.fetchone()[0]
            
            # Count orphaned nodes (nodes with invalid parent_id)
            cursor.execute("""
                SELECT COUNT(*) FROM nodes n
                WHERE n.parent_id IS NOT NULL 
                AND n.parent_id NOT IN (SELECT id FROM nodes WHERE id = n.parent_id)
            """)
            orphans = cursor.fetchone()[0]
            
            # Count duplicate labels (same label appearing multiple times at same depth)
            cursor.execute("""
                SELECT COUNT(*) FROM (
                    SELECT label, depth, COUNT(*) as label_count
                    FROM nodes
                    WHERE label IS NOT NULL
                    GROUP BY label, depth
                    HAVING label_count > 1
                ) as duplicates
            """)
            duplicate_paths = cursor.fetchone()[0]
            
            # Count total nodes for context
            cursor.execute("SELECT COUNT(*) FROM nodes")
            total_nodes = cursor.fetchone()[0]
            
            # Count total parents
            cursor.execute("SELECT COUNT(*) FROM nodes WHERE parent_id IS NULL")
            total_parents = cursor.fetchone()[0]
            
            return {
                "slot_gaps": slot_gaps,
                "over_5_children": over_5_children,
                "orphans": orphans,
                "duplicate_labels": duplicate_paths,
                "total_nodes": total_nodes,
                "total_parents": total_parents,
                "validation_rules": get_validation_rules(),
                "status": "healthy" if slot_gaps == 0 and over_5_children == 0 and orphans == 0 else "issues_detected"
            }
    
    except Exception as e:
        logging.error(f"Error getting data quality summary: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to get data quality summary",
                "message": str(e)
            }
        )

@router.post("/admin/data-quality/repair/slot-gaps")
async def repair_slot_gaps(repo: SQLiteRepository = Depends(get_repository)):
    """
    Repair slot gaps by filling missing slots with "Other" placeholder.
    
    This operation is:
    - Transactional (all or nothing)
    - Idempotent (safe to run multiple times)
    - Only fills slots where appropriate
    
    Returns:
        200 with repair summary
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            
            # Start transaction
            cursor.execute("BEGIN TRANSACTION")
            
            try:
                # Find parents with missing slots
                cursor.execute("""
                    SELECT parent_id, COUNT(*) as child_count
                    FROM nodes 
                    WHERE parent_id IS NOT NULL
                    GROUP BY parent_id
                    HAVING child_count < 5
                """)
                parents_with_gaps = cursor.fetchall()
                
                repaired_count = 0
                repair_details = []
                
                for parent_id, child_count in parents_with_gaps:
                    # Find which slots are missing
                    cursor.execute("""
                        SELECT slot FROM nodes 
                        WHERE parent_id = ? AND slot IS NOT NULL
                    """, (parent_id,))
                    existing_slots = {row[0] for row in cursor.fetchall()}
                    missing_slots = set(range(1, 6)) - existing_slots
                    
                    # Fill missing slots with "Other" placeholder
                    for slot in missing_slots:
                        # Get parent depth for child depth calculation
                        cursor.execute("SELECT depth FROM nodes WHERE id = ?", (parent_id,))
                        parent_depth = cursor.fetchone()
                        child_depth = (parent_depth[0] + 1) if parent_depth else 1
                        
                        # Insert placeholder child
                        cursor.execute("""
                            INSERT INTO nodes (parent_id, label, slot, depth, is_leaf)
                            VALUES (?, ?, ?, ?, ?)
                        """, (parent_id, "Other", slot, child_depth, 1))
                        
                        repaired_count += 1
                        repair_details.append({
                            "parent_id": parent_id,
                            "slot": slot,
                            "action": "filled_with_other"
                        })
                
                # Commit transaction
                cursor.execute("COMMIT")
                
                return {
                    "repaired_count": repaired_count,
                    "repair_details": repair_details,
                    "status": "completed",
                    "message": f"Successfully repaired {repaired_count} slot gaps"
                }
            
            except Exception as e:
                # Rollback on error
                cursor.execute("ROLLBACK")
                raise e
    
    except Exception as e:
        logging.error(f"Error repairing slot gaps: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to repair slot gaps",
                "message": str(e)
            }
        )

@router.get("/admin/data-quality/validation-rules")
async def get_validation_rules_endpoint():
    """
    Get current validation rules for documentation/debugging.
    
    Returns:
        200 with validation rules
    """
    return {
        "validation_rules": get_validation_rules(),
        "description": "Central validation rules used across the application"
    }
