"""
Dictionary router for medical term management.
Provides search, CRUD operations, export, and import functionality.
"""

import json
import sqlite3
from typing import Optional

import anyio
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from ..dependencies import get_db_connection
from ..services.dictionary_sync_service import DictionarySyncService
from ..services.dictionary_upload_service import DictionaryUploadService

router = APIRouter(prefix="/api/v1/dictionary", tags=["dictionary"])


async def _sync_red_flags_direct(conn: sqlite3.Connection, term: str, is_red_flag: bool):
    """Direct sync of red flag status to edge_meta table for VM Builder compatibility."""
    # Get all nodes with this term
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        """
        SELECT id FROM nodes
        WHERE LOWER(TRIM(label)) = LOWER(?)
        """,
        (term,),
    )
    node_ids = [row[0] for row in await anyio.to_thread.run_sync(cursor.fetchall)]

    if not node_ids:
        return

    # Update edge_meta table for VM Builder compatibility
    for node_id in node_ids:
        # Get parent_id for this node
        cursor = await anyio.to_thread.run_sync(
            conn.execute,
            """
            SELECT parent_id FROM nodes WHERE id = ?
            """,
            (node_id,),
        )
        parent_row = await anyio.to_thread.run_sync(cursor.fetchone)

        if parent_row and parent_row[0]:
            parent_id = parent_row[0]

            # Update or insert edge_meta entry
            await anyio.to_thread.run_sync(
                conn.execute,
                """
                INSERT INTO edge_meta(parent_id, child_id, red_flag)
                VALUES(?, ?, ?)
                ON CONFLICT(parent_id, child_id) DO UPDATE SET red_flag = excluded.red_flag
                """,
                (parent_id, node_id, 1 if is_red_flag else 0),
            )


# Pydantic models for request/response
class DictionaryTerm(BaseModel):
    id: int
    term: str
    definition: Optional[str] = None
    synonyms: list[str] = Field(default_factory=list)
    is_red_flag: bool = False
    avg_children_count: int = 0
    conflicts_count: int = 0
    created_at: str
    updated_at: str


class DictionaryTermUpdate(BaseModel):
    definition: Optional[str] = None
    synonyms: Optional[list[str]] = None
    is_red_flag: Optional[bool] = None


class DictionarySearchResult(BaseModel):
    items: list[DictionaryTerm]
    total: int
    query: str


class DictionaryExportRequest(BaseModel):
    format: str = Field(default="csv", pattern="^(csv|xlsx)$")
    include_synonyms: bool = True
    include_red_flags: bool = True


class DictionaryTermRename(BaseModel):
    new_term: str = Field(min_length=1, max_length=256)


class DictionaryTermMerge(BaseModel):
    target_term_id: int
    selected_children: list[str] = Field(default_factory=list)


# Helper functions
def _normalize_term(term: str) -> str:
    """Normalize term for consistent comparison."""
    return term.strip().lower()


def _parse_synonyms(synonyms_text: str) -> list[str]:
    """Parse synonyms from JSON text."""
    if not synonyms_text:
        return []
    try:
        return json.loads(synonyms_text)
    except json.JSONDecodeError:
        return []


def _serialize_synonyms(synonyms: list[str]) -> str:
    """Serialize synonyms to JSON text."""
    return json.dumps(synonyms)


def _dict_to_term(row: sqlite3.Row) -> DictionaryTerm:
    """Convert database row to DictionaryTerm model."""
    return DictionaryTerm(
        id=row["id"],
        term=row["term"],
        definition=row["definition"],
        synonyms=_parse_synonyms(row["synonyms"]),
        is_red_flag=bool(row["is_red_flag"]),
        avg_children_count=row["avg_children_count"],
        conflicts_count=row["conflicts_count"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# API Endpoints


@router.get("/search", response_model=DictionarySearchResult)
async def search_terms(
    q: str = Query(default="", description="Search query"),
    limit: int = Query(default=50, ge=1, le=200, description="Maximum results"),
    offset: int = Query(default=0, ge=0, description="Results offset"),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Search dictionary terms by name (case-insensitive partial matching)."""
    # Handle empty query by returning all terms
    if not q.strip():
        search_term = "%"
    else:
        search_term = f"%{q.strip()}%"

    # Count total results
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        """
        SELECT COUNT(*) as total
        FROM medical_dictionary
        WHERE LOWER(term) LIKE LOWER(?)
        """,
        (search_term,),
    )
    total_row = await anyio.to_thread.run_sync(cursor.fetchone)
    total = total_row["total"] if total_row else 0

    # Get results
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        """
        SELECT * FROM medical_dictionary
        WHERE LOWER(term) LIKE LOWER(?)
        ORDER BY term ASC
        LIMIT ? OFFSET ?
        """,
        (search_term, limit, offset),
    )
    rows = await anyio.to_thread.run_sync(cursor.fetchall)

    items = [_dict_to_term(row) for row in rows]

    return DictionarySearchResult(
        items=items,
        total=total,
        query=q,
    )


@router.get("/stats")
async def get_dictionary_stats(
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Get dictionary statistics and summary information."""
    # Total terms
    cursor = await anyio.to_thread.run_sync(
        conn.execute, "SELECT COUNT(*) as total FROM medical_dictionary"
    )
    total_terms = (await anyio.to_thread.run_sync(cursor.fetchone))["total"]

    # Red flag terms
    cursor = await anyio.to_thread.run_sync(
        conn.execute, "SELECT COUNT(*) as red_flags FROM medical_dictionary WHERE is_red_flag = 1"
    )
    red_flag_terms = (await anyio.to_thread.run_sync(cursor.fetchone))["red_flags"]

    # Terms with definitions
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT COUNT(*) as with_definitions FROM medical_dictionary WHERE definition IS NOT NULL AND definition != ''",
    )
    terms_with_definitions = (await anyio.to_thread.run_sync(cursor.fetchone))["with_definitions"]

    # Terms with synonyms
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT COUNT(*) as with_synonyms FROM medical_dictionary WHERE synonyms IS NOT NULL AND synonyms != '[]' AND synonyms != ''",
    )
    terms_with_synonyms = (await anyio.to_thread.run_sync(cursor.fetchone))["with_synonyms"]

    # Average children count
    cursor = await anyio.to_thread.run_sync(
        conn.execute, "SELECT AVG(avg_children_count) as avg_children FROM medical_dictionary"
    )
    avg_children = (await anyio.to_thread.run_sync(cursor.fetchone))["avg_children"] or 0

    # Total conflicts
    cursor = await anyio.to_thread.run_sync(
        conn.execute, "SELECT SUM(conflicts_count) as total_conflicts FROM medical_dictionary"
    )
    total_conflicts = (await anyio.to_thread.run_sync(cursor.fetchone))["total_conflicts"] or 0

    return {
        "total_terms": total_terms,
        "red_flag_terms": red_flag_terms,
        "terms_with_definitions": terms_with_definitions,
        "terms_with_synonyms": terms_with_synonyms,
        "avg_children_per_term": round(avg_children, 2),
        "total_conflicts": total_conflicts,
        "completion_rate": {
            "definitions": round((terms_with_definitions / total_terms * 100), 1)
            if total_terms > 0
            else 0,
            "synonyms": round((terms_with_synonyms / total_terms * 100), 1)
            if total_terms > 0
            else 0,
        },
    }


@router.get("/{term_id}", response_model=DictionaryTerm)
async def get_term(
    term_id: int,
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Get detailed information about a specific dictionary term."""
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT * FROM medical_dictionary WHERE id = ?",
        (term_id,),
    )
    row = await anyio.to_thread.run_sync(cursor.fetchone)

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dictionary term with id {term_id} not found",
        )

    return _dict_to_term(row)


@router.get("/term/{term_name}", response_model=DictionaryTerm)
async def get_term_by_name(
    term_name: str,
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Get dictionary term by name (case-insensitive)."""
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT * FROM medical_dictionary WHERE LOWER(term) = LOWER(?)",
        (term_name.strip(),),
    )
    row = await anyio.to_thread.run_sync(cursor.fetchone)

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Dictionary term '{term_name}' not found"
        )

    return _dict_to_term(row)


@router.put("/{term_id}", response_model=DictionaryTerm)
async def update_term(
    term_id: int,
    update_data: DictionaryTermUpdate,
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Update dictionary term definition, synonyms, or red-flag status with bidirectional sync."""
    # Get current term data
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT * FROM medical_dictionary WHERE id = ?",
        (term_id,),
    )
    current_term = await anyio.to_thread.run_sync(cursor.fetchone)

    if not current_term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dictionary term with id {term_id} not found",
        )

    old_term = current_term["term"]

    # Initialize sync service
    sync_service = DictionarySyncService(conn)

    # If term name is being changed, validate the update
    new_term = update_data.term if hasattr(update_data, "term") and update_data.term else old_term
    if new_term != old_term:
        validation = await sync_service.validate_dictionary_update(term_id, new_term, old_term)
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "errors": validation["errors"],
                    "warnings": validation["warnings"],
                },
            )

    # Build update query dynamically
    updates = []
    params = []

    # Handle term name change (if supported)
    if hasattr(update_data, "term") and update_data.term and update_data.term != old_term:
        updates.append("term = ?")
        params.append(update_data.term)

    if update_data.definition is not None:
        updates.append("definition = ?")
        params.append(update_data.definition)

    if update_data.synonyms is not None:
        updates.append("synonyms = ?")
        params.append(_serialize_synonyms(update_data.synonyms))

    if update_data.is_red_flag is not None:
        updates.append("is_red_flag = ?")
        params.append(int(update_data.is_red_flag))

    if not updates:
        # No changes requested
        return _dict_to_term(current_term)

    # Add term_id to params and execute update
    params.append(term_id)
    update_query = f"UPDATE medical_dictionary SET {', '.join(updates)} WHERE id = ?"

    await anyio.to_thread.run_sync(
        conn.execute,
        update_query,
        params,
    )

    # Sync changes to tree nodes if needed
    if new_term != old_term:
        await sync_service.sync_nodes_from_dictionary(
            old_term=old_term,
            new_term=new_term,
            definition=update_data.definition,
            synonyms=update_data.synonyms,
            is_red_flag=update_data.is_red_flag,
        )
    elif update_data.is_red_flag is not None:
        # Just sync red flag status - direct approach
        await _sync_red_flags_direct(conn, new_term, update_data.is_red_flag)

    # Return updated term
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT * FROM medical_dictionary WHERE id = ?",
        (term_id,),
    )
    row = await anyio.to_thread.run_sync(cursor.fetchone)

    return _dict_to_term(row)


@router.get("/export/csv")
async def export_dictionary_csv(
    include_synonyms: bool = Query(default=True),
    include_red_flags: bool = Query(default=True),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Export dictionary as CSV file."""
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        """
        SELECT term, definition, synonyms, is_red_flag, avg_children_count, conflicts_count
        FROM medical_dictionary
        ORDER BY term ASC
        """,
    )
    rows = await anyio.to_thread.run_sync(cursor.fetchall)

    # Build CSV content
    csv_lines = []

    # Header
    header = ["Term", "Definition"]
    if include_synonyms:
        header.append("Synonyms")
    if include_red_flags:
        header.append("Red Flag")
    header.extend(["Avg Children Count", "Conflicts Count"])

    csv_lines.append(",".join(f'"{col}"' for col in header))

    # Data rows
    for row in rows:
        csv_row = [f'"{row["term"]}"', f'"{row["definition"] or ""}"']

        if include_synonyms:
            synonyms = _parse_synonyms(row["synonyms"])
            csv_row.append(f'"{"; ".join(synonyms)}"')

        if include_red_flags:
            csv_row.append("Yes" if row["is_red_flag"] else "No")

        csv_row.extend([str(row["avg_children_count"]), str(row["conflicts_count"])])

        csv_lines.append(",".join(csv_row))

    csv_content = "\n".join(csv_lines)

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=medical_dictionary.csv"},
    )


@router.post("/upload")
async def upload_dictionary(
    file: UploadFile = File(...),
    update_existing: bool = Query(default=True, description="Update existing dictionary terms"),
    create_new_terms: bool = Query(default=True, description="Create new terms not in dictionary"),
    min_similarity: float = Query(
        default=0.8, ge=0.0, le=1.0, description="Minimum similarity for spelling suggestions"
    ),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Upload medical dictionary file (CSV/XLSX) to find matches, fill definitions, and detect spelling errors."""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided")

    if not file.filename.lower().endswith((".csv", ".xlsx")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be CSV or XLSX format"
        )

    try:
        file_content = await file.read()
        upload_service = DictionaryUploadService(conn)

        result = await upload_service.process_dictionary_upload(
            file_content=file_content,
            filename=file.filename,
            update_existing=update_existing,
            create_new_terms=create_new_terms,
            min_similarity=min_similarity,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload processing failed: {str(e)}",
        )


@router.post("/upload/validate")
async def validate_dictionary_file(
    file: UploadFile = File(...),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Validate a medical dictionary file before uploading."""
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No filename provided")

    if not file.filename.lower().endswith((".csv", ".xlsx")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be CSV or XLSX format"
        )

    try:
        file_content = await file.read()
        upload_service = DictionaryUploadService(conn)

        validation_result = await upload_service.validate_dictionary_file(
            file_content=file_content, filename=file.filename
        )

        return validation_result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File validation failed: {str(e)}",
        )


@router.get("/tree/{term_id}/relationships")
async def get_term_tree_relationships(
    term_id: int,
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Get tree relationships for a dictionary term (parents and children)."""
    # Get the term
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT term FROM medical_dictionary WHERE id = ?",
        (term_id,),
    )
    term_row = await anyio.to_thread.run_sync(cursor.fetchone)

    if not term_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dictionary term with id {term_id} not found",
        )

    term_name = term_row["term"]

    # Find all nodes with this term
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        """
        SELECT id, depth, slot, parent_id
        FROM nodes
        WHERE LOWER(TRIM(label)) = LOWER(?)
        ORDER BY depth, id
        """,
        (term_name,),
    )
    nodes = await anyio.to_thread.run_sync(cursor.fetchall)

    # Get parents (nodes that have this term as a child)
    parent_ids = [node["parent_id"] for node in nodes if node["parent_id"]]
    parents = []
    if parent_ids:
        placeholders = ",".join("?" * len(parent_ids))
        cursor = await anyio.to_thread.run_sync(
            conn.execute,
            f"""
            SELECT id, label, depth, slot
            FROM nodes
            WHERE id IN ({placeholders})
            ORDER BY depth, id
            """,
            parent_ids,
        )
        parents = await anyio.to_thread.run_sync(cursor.fetchall)

    # Get children (nodes that are children of nodes with this term)
    children = []
    for node in nodes:
        cursor = await anyio.to_thread.run_sync(
            conn.execute,
            """
            SELECT id, label, depth, slot
            FROM nodes
            WHERE parent_id = ?
            ORDER BY slot, id
            """,
            (node["id"],),
        )
        node_children = await anyio.to_thread.run_sync(cursor.fetchall)
        children.extend(node_children)

    # Remove duplicates and sort
    children = list({child["id"]: child for child in children}.values())
    children.sort(key=lambda x: (x["depth"], x["slot"], x["id"]))

    return {
        "term": term_name,
        "nodes": [
            {
                "id": node["id"],
                "depth": node["depth"],
                "slot": node["slot"],
                "parent_id": node["parent_id"],
            }
            for node in nodes
        ],
        "parents": [
            {
                "id": parent["id"],
                "label": parent["label"],
                "depth": parent["depth"],
                "slot": parent["slot"],
            }
            for parent in parents
        ],
        "children": [
            {
                "id": child["id"],
                "label": child["label"],
                "depth": child["depth"],
                "slot": child["slot"],
            }
            for child in children
        ],
    }


@router.get("/{term_id}/sync-status")
async def get_term_sync_status(
    term_id: int,
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Get the sync status between dictionary and tree nodes for a term."""
    # Get the term
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT term FROM medical_dictionary WHERE id = ?",
        (term_id,),
    )
    term_row = await anyio.to_thread.run_sync(cursor.fetchone)

    if not term_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dictionary term with id {term_id} not found",
        )

    term_name = term_row["term"]
    sync_service = DictionarySyncService(conn)

    return await sync_service.get_sync_status(term_name)


@router.post("/{term_id}/validate-update")
async def validate_term_update(
    term_id: int,
    update_data: DictionaryTermUpdate,
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Validate a potential dictionary update to check for conflicts."""
    # Get current term
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT term FROM medical_dictionary WHERE id = ?",
        (term_id,),
    )
    term_row = await anyio.to_thread.run_sync(cursor.fetchone)

    if not term_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dictionary term with id {term_id} not found",
        )

    old_term = term_row["term"]
    new_term = getattr(update_data, "term", old_term)

    sync_service = DictionarySyncService(conn)
    return await sync_service.validate_dictionary_update(term_id, new_term, old_term)


@router.put("/{term_id}/rename")
async def rename_dictionary_term(
    term_id: int,
    rename_data: DictionaryTermRename,
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Rename a dictionary term and sync changes to tree nodes."""
    new_term = rename_data.new_term.strip()

    if not new_term:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Term name cannot be empty"
        )

    # Get current term
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT term FROM medical_dictionary WHERE id = ?",
        (term_id,),
    )
    term_row = await anyio.to_thread.run_sync(cursor.fetchone)

    if not term_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dictionary term with id {term_id} not found",
        )

    old_term = term_row["term"]

    # Check if new term already exists
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT id FROM medical_dictionary WHERE LOWER(TRIM(term)) = LOWER(TRIM(?)) AND id != ?",
        (new_term, term_id),
    )
    existing_row = await anyio.to_thread.run_sync(cursor.fetchone)

    if existing_row:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Term '{new_term}' already exists. Use merge operation instead.",
        )

    try:
        # Temporarily disable dictionary sync triggers to avoid conflicts
        await anyio.to_thread.run_sync(
            conn.execute, "DROP TRIGGER IF EXISTS tr_sync_dictionary_on_node_change"
        )
        await anyio.to_thread.run_sync(
            conn.execute, "DROP TRIGGER IF EXISTS tr_sync_dictionary_on_node_insert"
        )
        await anyio.to_thread.run_sync(
            conn.execute, "DROP TRIGGER IF EXISTS tr_sync_nodes_on_dictionary_change"
        )

        # Update dictionary term
        await anyio.to_thread.run_sync(
            conn.execute,
            "UPDATE medical_dictionary SET term = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id = ?",
            (new_term, term_id),
        )

        # Update all nodes that use the old term to use the new term
        await anyio.to_thread.run_sync(
            conn.execute,
            "UPDATE nodes SET label = ? WHERE LOWER(TRIM(label)) = LOWER(TRIM(?))",
            (new_term, old_term),
        )

        # Re-enable the dictionary sync triggers
        await anyio.to_thread.run_sync(
            conn.execute,
            """
            CREATE TRIGGER IF NOT EXISTS tr_sync_dictionary_on_node_change
            AFTER UPDATE OF label, is_red_flag ON nodes
            FOR EACH ROW
            BEGIN
                UPDATE medical_dictionary
                SET
                    avg_children_count = (SELECT COUNT(*) FROM nodes WHERE parent_id = NEW.id),
                    conflicts_count = (SELECT COUNT(*) FROM conflicts WHERE node_id = NEW.id),
                    is_red_flag = (SELECT MAX(is_red_flag) FROM nodes WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label)))
                WHERE LOWER(TRIM(term)) = LOWER(TRIM(NEW.label));
            END;
        """,
        )

        await anyio.to_thread.run_sync(
            conn.execute,
            """
            CREATE TRIGGER IF NOT EXISTS tr_sync_dictionary_on_node_insert
            AFTER INSERT ON nodes
            FOR EACH ROW
            BEGIN
                INSERT OR IGNORE INTO medical_dictionary (term, avg_children_count, conflicts_count, is_red_flag)
                VALUES (
                    NEW.label,
                    (SELECT COUNT(*) FROM nodes WHERE parent_id = NEW.id),
                    (SELECT COUNT(*) FROM conflicts WHERE node_id = NEW.id),
                    NEW.is_red_flag
                );
                UPDATE medical_dictionary
                SET
                    avg_children_count = (SELECT COUNT(*) FROM nodes WHERE parent_id = NEW.id),
                    conflicts_count = (SELECT COUNT(*) FROM conflicts WHERE node_id = NEW.id),
                    is_red_flag = (SELECT MAX(is_red_flag) FROM nodes WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label)))
                WHERE LOWER(TRIM(term)) = LOWER(TRIM(NEW.label));
            END;
        """,
        )

        await anyio.to_thread.run_sync(
            conn.execute,
            """
            CREATE TRIGGER IF NOT EXISTS tr_sync_nodes_on_dictionary_change
            AFTER UPDATE OF term ON medical_dictionary
            FOR EACH ROW
            WHEN NEW.term != OLD.term
            BEGIN
                UPDATE nodes
                SET label = NEW.term
                WHERE LOWER(TRIM(label)) = LOWER(TRIM(OLD.term));
            END;
        """,
        )

    except Exception as e:
        # Re-enable triggers even on error
        try:
            await anyio.to_thread.run_sync(
                conn.execute,
                """
                CREATE TRIGGER IF NOT EXISTS tr_sync_dictionary_on_node_change
                AFTER UPDATE OF label, is_red_flag ON nodes
                FOR EACH ROW
                BEGIN
                    UPDATE medical_dictionary
                    SET
                        avg_children_count = (SELECT COUNT(*) FROM nodes WHERE parent_id = NEW.id),
                        conflicts_count = (SELECT COUNT(*) FROM conflicts WHERE node_id = NEW.id),
                        is_red_flag = (SELECT MAX(is_red_flag) FROM nodes WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label)))
                    WHERE LOWER(TRIM(term)) = LOWER(TRIM(NEW.label));
                END;
            """,
            )

            await anyio.to_thread.run_sync(
                conn.execute,
                """
                CREATE TRIGGER IF NOT EXISTS tr_sync_dictionary_on_node_insert
                AFTER INSERT ON nodes
                FOR EACH ROW
                BEGIN
                    INSERT OR IGNORE INTO medical_dictionary (term, avg_children_count, conflicts_count, is_red_flag)
                    VALUES (
                        NEW.label,
                        (SELECT COUNT(*) FROM nodes WHERE parent_id = NEW.id),
                        (SELECT COUNT(*) FROM conflicts WHERE node_id = NEW.id),
                        NEW.is_red_flag
                    );
                    UPDATE medical_dictionary
                    SET
                        avg_children_count = (SELECT COUNT(*) FROM nodes WHERE parent_id = NEW.id),
                        conflicts_count = (SELECT COUNT(*) FROM conflicts WHERE node_id = NEW.id),
                        is_red_flag = (SELECT MAX(is_red_flag) FROM nodes WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label)))
                    WHERE LOWER(TRIM(term)) = LOWER(TRIM(NEW.label));
                END;
            """,
            )

            await anyio.to_thread.run_sync(
                conn.execute,
                """
                CREATE TRIGGER IF NOT EXISTS tr_sync_nodes_on_dictionary_change
                AFTER UPDATE OF term ON medical_dictionary
                FOR EACH ROW
                WHEN NEW.term != OLD.term
                BEGIN
                    UPDATE nodes
                    SET label = NEW.term
                    WHERE LOWER(TRIM(label)) = LOWER(TRIM(OLD.term));
                END;
            """,
            )
        except:
            pass  # Ignore trigger recreation errors during rollback

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Rename failed: {str(e)}"
        )

    # Return updated term
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT * FROM medical_dictionary WHERE id = ?",
        (term_id,),
    )
    term_row = await anyio.to_thread.run_sync(cursor.fetchone)

    return DictionaryTerm(
        id=term_row["id"],
        term=term_row["term"],
        definition=term_row["definition"],
        synonyms=json.loads(term_row["synonyms"]) if term_row["synonyms"] else [],
        is_red_flag=bool(term_row["is_red_flag"]),
        avg_children_count=term_row["avg_children_count"],
        conflicts_count=term_row["conflicts_count"],
        created_at=term_row["created_at"],
        updated_at=term_row["updated_at"],
    )


@router.post("/{term_id}/merge")
async def merge_dictionary_terms(
    term_id: int,
    merge_data: DictionaryTermMerge,
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Merge two dictionary terms by combining their children and deleting the source term."""
    target_term_id = merge_data.target_term_id
    selected_children = merge_data.selected_children

    if len(selected_children) > 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Cannot have more than 5 children",
        )

    # Get source and target terms
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT id, term FROM medical_dictionary WHERE id IN (?, ?)",
        (term_id, target_term_id),
    )
    rows = await anyio.to_thread.run_sync(cursor.fetchall)

    if len(rows) != 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="One or both dictionary terms not found"
        )

    source_term = None
    target_term = None
    for row in rows:
        if row["id"] == term_id:
            source_term = row["term"]
        elif row["id"] == target_term_id:
            target_term = row["term"]

    if not source_term or not target_term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source or target term not found"
        )

    try:
        # Temporarily disable dictionary sync triggers to avoid conflicts
        await anyio.to_thread.run_sync(
            conn.execute, "DROP TRIGGER IF EXISTS tr_sync_dictionary_on_node_change"
        )
        await anyio.to_thread.run_sync(
            conn.execute, "DROP TRIGGER IF EXISTS tr_sync_dictionary_on_node_insert"
        )
        await anyio.to_thread.run_sync(
            conn.execute, "DROP TRIGGER IF EXISTS tr_sync_nodes_on_dictionary_change"
        )

        # Get all nodes that use the source term
        cursor = await anyio.to_thread.run_sync(
            conn.execute,
            "SELECT id, parent_id, depth FROM nodes WHERE LOWER(TRIM(label)) = LOWER(TRIM(?))",
            (source_term,),
        )
        source_nodes = await anyio.to_thread.run_sync(cursor.fetchall)

        # Get all nodes that use the target term
        cursor = await anyio.to_thread.run_sync(
            conn.execute,
            "SELECT id, parent_id, depth FROM nodes WHERE LOWER(TRIM(label)) = LOWER(TRIM(?))",
            (target_term,),
        )
        target_nodes = await anyio.to_thread.run_sync(cursor.fetchall)

        # For each source node, merge its children into the corresponding target node
        for source_node in source_nodes:
            source_node_id = source_node["id"]
            source_parent_id = source_node["parent_id"]
            source_depth = source_node["depth"]

            # Find corresponding target node with same parent and depth
            target_node_id = None
            for target_node in target_nodes:
                if (
                    target_node["parent_id"] == source_parent_id
                    and target_node["depth"] == source_depth
                ):
                    target_node_id = target_node["id"]
                    break

            if not target_node_id:
                # If no corresponding target node, just rename the source node
                await anyio.to_thread.run_sync(
                    conn.execute,
                    "UPDATE nodes SET label = ? WHERE id = ?",
                    (target_term, source_node_id),
                )
            else:
                # Get children of source node
                cursor = await anyio.to_thread.run_sync(
                    conn.execute,
                    "SELECT label FROM nodes WHERE parent_id = ? ORDER BY slot",
                    (source_node_id,),
                )
                source_children = await anyio.to_thread.run_sync(cursor.fetchall)

                # Get children of target node
                cursor = await anyio.to_thread.run_sync(
                    conn.execute,
                    "SELECT label FROM nodes WHERE parent_id = ? ORDER BY slot",
                    (target_node_id,),
                )
                target_children = await anyio.to_thread.run_sync(cursor.fetchall)

                # Combine children (use selected_children if provided, otherwise combine all)
                if selected_children:
                    combined_children = selected_children
                else:
                    combined_children = [child["label"] for child in target_children]
                    for child in source_children:
                        if child["label"] not in combined_children:
                            combined_children.append(child["label"])

                if len(combined_children) > 5:
                    # If too many children, truncate to 5
                    combined_children = combined_children[:5]

                # Delete all children from target node
                await anyio.to_thread.run_sync(
                    conn.execute,
                    "DELETE FROM nodes WHERE parent_id = ?",
                    (target_node_id,),
                )

                # Add combined children to target node
                for i, child_label in enumerate(combined_children, 1):
                    child_depth = source_depth + 1
                    is_leaf = 1 if child_depth >= 5 else 0

                    await anyio.to_thread.run_sync(
                        conn.execute,
                        """INSERT INTO nodes (parent_id, depth, slot, label, is_leaf, created_at, updated_at)
                           VALUES (?, ?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%fZ','now'), strftime('%Y-%m-%dT%H:%M:%fZ','now'))""",
                        (target_node_id, child_depth, i, child_label, is_leaf),
                    )

                # Delete the source node and its remaining children
                await anyio.to_thread.run_sync(
                    conn.execute,
                    "DELETE FROM nodes WHERE id = ?",
                    (source_node_id,),
                )

        # Delete the source dictionary term BEFORE re-enabling triggers
        await anyio.to_thread.run_sync(
            conn.execute,
            "DELETE FROM medical_dictionary WHERE id = ?",
            (term_id,),
        )

        # Re-enable the dictionary sync triggers
        await anyio.to_thread.run_sync(
            conn.execute,
            """
            CREATE TRIGGER IF NOT EXISTS tr_sync_dictionary_on_node_change
            AFTER UPDATE OF label, is_red_flag ON nodes
            FOR EACH ROW
            BEGIN
                UPDATE medical_dictionary
                SET
                    avg_children_count = (SELECT COUNT(*) FROM nodes WHERE parent_id = NEW.id),
                    conflicts_count = (SELECT COUNT(*) FROM conflicts WHERE node_id = NEW.id),
                    is_red_flag = (SELECT MAX(is_red_flag) FROM nodes WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label)))
                WHERE LOWER(TRIM(term)) = LOWER(TRIM(NEW.label));
            END;
        """,
        )

        await anyio.to_thread.run_sync(
            conn.execute,
            """
            CREATE TRIGGER IF NOT EXISTS tr_sync_dictionary_on_node_insert
            AFTER INSERT ON nodes
            FOR EACH ROW
            BEGIN
                INSERT OR IGNORE INTO medical_dictionary (term, avg_children_count, conflicts_count, is_red_flag)
                VALUES (
                    NEW.label,
                    (SELECT COUNT(*) FROM nodes WHERE parent_id = NEW.id),
                    (SELECT COUNT(*) FROM conflicts WHERE node_id = NEW.id),
                    NEW.is_red_flag
                );
                UPDATE medical_dictionary
                SET
                    avg_children_count = (SELECT COUNT(*) FROM nodes WHERE parent_id = NEW.id),
                    conflicts_count = (SELECT COUNT(*) FROM conflicts WHERE node_id = NEW.id),
                    is_red_flag = (SELECT MAX(is_red_flag) FROM nodes WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label)))
                WHERE LOWER(TRIM(term)) = LOWER(TRIM(NEW.label));
            END;
        """,
        )

        await anyio.to_thread.run_sync(
            conn.execute,
            """
            CREATE TRIGGER IF NOT EXISTS tr_sync_nodes_on_dictionary_change
            AFTER UPDATE OF term ON medical_dictionary
            FOR EACH ROW
            WHEN NEW.term != OLD.term
            BEGIN
                UPDATE nodes
                SET label = NEW.term
                WHERE LOWER(TRIM(label)) = LOWER(TRIM(OLD.term));
            END;
        """,
        )

        # Update target dictionary term metrics
        sync_service = DictionarySyncService(conn)
        await sync_service.sync_dictionary_metrics(target_term)

    except Exception as e:
        # Re-enable triggers even on error
        try:
            await anyio.to_thread.run_sync(
                conn.execute,
                """
                CREATE TRIGGER IF NOT EXISTS tr_sync_dictionary_on_node_change
                AFTER UPDATE OF label, is_red_flag ON nodes
                FOR EACH ROW
                BEGIN
                    UPDATE medical_dictionary
                    SET
                        avg_children_count = (SELECT COUNT(*) FROM nodes WHERE parent_id = NEW.id),
                        conflicts_count = (SELECT COUNT(*) FROM conflicts WHERE node_id = NEW.id),
                        is_red_flag = (SELECT MAX(is_red_flag) FROM nodes WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label)))
                    WHERE LOWER(TRIM(term)) = LOWER(TRIM(NEW.label));
                END;
            """,
            )

            await anyio.to_thread.run_sync(
                conn.execute,
                """
                CREATE TRIGGER IF NOT EXISTS tr_sync_dictionary_on_node_insert
                AFTER INSERT ON nodes
                FOR EACH ROW
                BEGIN
                    INSERT OR IGNORE INTO medical_dictionary (term, avg_children_count, conflicts_count, is_red_flag)
                    VALUES (
                        NEW.label,
                        (SELECT COUNT(*) FROM nodes WHERE parent_id = NEW.id),
                        (SELECT COUNT(*) FROM conflicts WHERE node_id = NEW.id),
                        NEW.is_red_flag
                    );
                    UPDATE medical_dictionary
                    SET
                        avg_children_count = (SELECT COUNT(*) FROM nodes WHERE parent_id = NEW.id),
                        conflicts_count = (SELECT COUNT(*) FROM conflicts WHERE node_id = NEW.id),
                        is_red_flag = (SELECT MAX(is_red_flag) FROM nodes WHERE LOWER(TRIM(label)) = LOWER(TRIM(NEW.label)))
                    WHERE LOWER(TRIM(term)) = LOWER(TRIM(NEW.label));
                END;
            """,
            )

            await anyio.to_thread.run_sync(
                conn.execute,
                """
                CREATE TRIGGER IF NOT EXISTS tr_sync_nodes_on_dictionary_change
                AFTER UPDATE OF term ON medical_dictionary
                FOR EACH ROW
                WHEN NEW.term != OLD.term
                BEGIN
                    UPDATE nodes
                    SET label = NEW.term
                    WHERE LOWER(TRIM(label)) = LOWER(TRIM(OLD.term));
                END;
            """,
            )
        except:
            pass  # Ignore trigger recreation errors during rollback

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Merge failed: {str(e)}"
        )

    # Return the target term details
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT * FROM medical_dictionary WHERE id = ?",
        (target_term_id,),
    )
    term_row = await anyio.to_thread.run_sync(cursor.fetchone)

    return {
        "ok": True,
        "merged_term_id": target_term_id,
        "deleted_term_id": term_id,
        "term": DictionaryTerm(
            id=term_row["id"],
            term=term_row["term"],
            definition=term_row["definition"],
            synonyms=json.loads(term_row["synonyms"]) if term_row["synonyms"] else [],
            is_red_flag=bool(term_row["is_red_flag"]),
            avg_children_count=term_row["avg_children_count"],
            conflicts_count=term_row["conflicts_count"],
            created_at=term_row["created_at"],
            updated_at=term_row["updated_at"],
        ),
    }


@router.get("/{term_id}/rename-conflicts")
async def get_rename_conflicts(
    term_id: int,
    new_term: str = Query(..., description="New term name to check for conflicts"),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Get conflicts that would occur when renaming a dictionary term."""
    # Get current term
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT term FROM medical_dictionary WHERE id = ?",
        (term_id,),
    )
    term_row = await anyio.to_thread.run_sync(cursor.fetchone)

    if not term_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dictionary term with id {term_id} not found",
        )

    old_term = term_row["term"]
    new_term = new_term.strip()

    if not new_term:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="New term name cannot be empty"
        )

    # Check if new term already exists
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT id, term FROM medical_dictionary WHERE LOWER(TRIM(term)) = LOWER(TRIM(?)) AND id != ?",
        (new_term, term_id),
    )
    existing_row = await anyio.to_thread.run_sync(cursor.fetchone)

    conflicts = {
        "has_conflicts": False,
        "conflict_type": None,
        "conflict_details": None,
        "affected_nodes": 0,
    }

    if existing_row:
        conflicts["has_conflicts"] = True
        conflicts["conflict_type"] = "duplicate_term"
        conflicts[
            "conflict_details"
        ] = f"Term '{new_term}' already exists (ID: {existing_row['id']})"

        # Count affected nodes
        cursor = await anyio.to_thread.run_sync(
            conn.execute,
            "SELECT COUNT(*) FROM nodes WHERE LOWER(TRIM(label)) = LOWER(TRIM(?))",
            (old_term,),
        )
        node_count = await anyio.to_thread.run_sync(cursor.fetchone)
        conflicts["affected_nodes"] = node_count[0]
    else:
        # Count nodes that would be affected by the rename
        cursor = await anyio.to_thread.run_sync(
            conn.execute,
            "SELECT COUNT(*) FROM nodes WHERE LOWER(TRIM(label)) = LOWER(TRIM(?))",
            (old_term,),
        )
        node_count = await anyio.to_thread.run_sync(cursor.fetchone)
        conflicts["affected_nodes"] = node_count[0]

    return conflicts


@router.get("/{term_id}/merge-conflicts")
async def get_merge_conflicts(
    term_id: int,
    target_term_id: int = Query(..., description="Target term ID to merge into"),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Get conflicts that would occur when merging dictionary terms."""
    # Get source and target terms
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        "SELECT id, term FROM medical_dictionary WHERE id IN (?, ?)",
        (term_id, target_term_id),
    )
    rows = await anyio.to_thread.run_sync(cursor.fetchall)

    if len(rows) != 2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source or target dictionary term not found",
        )

    source_term = None
    target_term = None
    for row in rows:
        if row["id"] == term_id:
            source_term = row["term"]
        elif row["id"] == target_term_id:
            target_term = row["term"]

    if not source_term or not target_term:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Source or target term not found"
        )

    # Get nodes for both terms
    cursor = await anyio.to_thread.run_sync(
        conn.execute,
        """SELECT n.id, n.parent_id, n.depth, n.label,
                  GROUP_CONCAT(c.label, ', ') as children
           FROM nodes n
           LEFT JOIN nodes c ON c.parent_id = n.id
           WHERE LOWER(TRIM(n.label)) IN (LOWER(TRIM(?)), LOWER(TRIM(?)))
           GROUP BY n.id, n.parent_id, n.depth, n.label
           ORDER BY n.depth, n.parent_id""",
        (source_term, target_term),
    )
    nodes = await anyio.to_thread.run_sync(cursor.fetchall)

    # Organize by term
    source_nodes = []
    target_nodes = []
    union_children = set()

    for node in nodes:
        if node["label"] == source_term:
            source_nodes.append(
                {
                    "id": node["id"],
                    "parent_id": node["parent_id"],
                    "depth": node["depth"],
                    "children": node["children"].split(", ") if node["children"] else [],
                }
            )
            if node["children"]:
                union_children.update(node["children"].split(", "))
        elif node["label"] == target_term:
            target_nodes.append(
                {
                    "id": node["id"],
                    "parent_id": node["parent_id"],
                    "depth": node["depth"],
                    "children": node["children"].split(", ") if node["children"] else [],
                }
            )
            if node["children"]:
                union_children.update(node["children"].split(", "))

    conflicts = {
        "source_term": source_term,
        "target_term": target_term,
        "source_nodes": source_nodes,
        "target_nodes": target_nodes,
        "union_children": list(union_children),
        "has_conflicts": len(union_children) > 5,
        "max_children_exceeded": len(union_children) > 5,
        "total_children": len(union_children),
    }

    return conflicts
