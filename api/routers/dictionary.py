"""
Dictionary router for medical term administration.
"""

from fastapi import APIRouter, HTTPException, Query, Depends, UploadFile, File
from pydantic import BaseModel, Field, constr
from typing import List, Optional, Literal
import sqlite3
import logging
import re
from datetime import datetime, timezone
import pandas as pd

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository

router = APIRouter(prefix="/dictionary", tags=["dictionary"])
logger = logging.getLogger(__name__)

# Locked dictionary types
DictType = Literal["vital_measurement", "node_label", "outcome_template"]


def _normalize(s: str) -> str:
    """Normalize term: lowercase + internal whitespace collapsed + trimmed."""
    return re.sub(r"\s+", " ", (s or "").strip()).lower()


class TermIn(BaseModel):
    type: DictType
    term: constr(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9 ,\-]+$")
    hints: Optional[constr(max_length=256)] = None
    red_flag: Optional[bool] = False


class TermOut(BaseModel):
    id: int
    type: DictType
    term: str
    normalized: str
    hints: Optional[str] = None
    red_flag: Optional[bool] = None
    updated_at: str


class UsageResponse(BaseModel):
    node_id: int
    path: str
    depth: int
@router.get("", response_model=List[TermOut])
def list_terms(
    type: Optional[DictType] = Query(None, description="Filter by type"),
    query: str = Query("", description="Search query for terms"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort: str = Query("label", description="Sort field"),
    direction: str = Query("asc", description="Sort direction"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    List dictionary terms with search, filtering, and pagination.

    For type=node_label with query, this provides autocomplete suggestions.
    Query must be ≥2 characters for performance.
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()

            # Build query
            sql = "SELECT id, category as type, label as term, normalized, hints, red_flag, updated_at FROM dictionary_terms"
            params = []
            conditions = []

            if type:
                conditions.append("category = ?")
                params.append(type)

            if query:
                # For node_label suggestions, enforce minimum query length
                if type == "node_label" and len(query.strip()) < 2:
                    return []  # Return empty for short queries

                conditions.append("(label LIKE ? OR normalized LIKE ?)")
                like_query = f"%{query}%"
                params.extend([like_query, like_query])

            if conditions:
                sql += " WHERE " + " AND ".join(conditions)

            # Sort options
            if sort == "label":
                sort_field = "label"
            elif sort == "type":
                sort_field = "category"
            else:
                sort_field = "label"

            sql += f" ORDER BY {sort_field} {direction} LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            return [
                TermOut(
                    id=row[0],
                    type=row[1],
                    term=row[2],
                    normalized=row[3],
                    hints=row[4],
                    red_flag=bool(row[5]) if row[5] is not None else None,
                    updated_at=row[6]
                )
                for row in rows
            ]

    except Exception as e:
        logger.exception("Error listing dictionary terms")
        raise HTTPException(status_code=500, detail="Database error")


@router.post("", status_code=201, response_model=TermOut)
def create_term(body: TermIn, repo: SQLiteRepository = Depends(get_repository)):
    """
    Create a new dictionary term.
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()

            # Normalize term
            normalized = _normalize(body.term)

            # Check for duplicate (category, normalized)
            cursor.execute(
                "SELECT id FROM dictionary_terms WHERE category = ? AND normalized = ?",
                (body.type, normalized)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=422,
                    detail=[{
                        "loc": ["body", "term"],
                        "msg": "Term already exists for this type",
                        "type": "value_error.duplicate"
                    }]
                )

            # Create term
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            cursor.execute("""
                INSERT INTO dictionary_terms (category, label, normalized, hints, red_flag, updated_at, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (body.type, body.term, normalized, body.hints, body.red_flag, now, now))

            term_id = cursor.lastrowid
            conn.commit()

            # Return created term
            cursor.execute(
                "SELECT id, category as type, label as term, normalized, hints, red_flag, updated_at FROM dictionary_terms WHERE id = ?",
                (term_id,)
            )
            row = cursor.fetchone()

            return TermOut(
                id=row[0],
                type=row[1],
                term=row[2],
                normalized=row[3],
                hints=row[4],
                red_flag=bool(row[5]) if row[5] is not None else None,
                updated_at=row[6]
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error creating dictionary term")
        raise HTTPException(status_code=500, detail="Database error")


@router.put("/{term_id}", response_model=TermOut)
def update_term(term_id: int, body: TermIn, repo: SQLiteRepository = Depends(get_repository)):
    """
    Update an existing dictionary term.
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()

            # Check if term exists
            cursor.execute("SELECT id FROM dictionary_terms WHERE id = ?", (term_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Term not found")

            # Normalize term
            normalized = _normalize(body.term)

            # Check for duplicate (category, normalized) (excluding current term)
            cursor.execute(
                "SELECT id FROM dictionary_terms WHERE category = ? AND normalized = ? AND id != ?",
                (body.type, normalized, term_id)
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=422,
                    detail=[{
                        "loc": ["body", "term"],
                        "msg": "Term already exists for this type",
                        "type": "value_error.duplicate"
                    }]
                )

            # Update term
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            cursor.execute("""
                UPDATE dictionary_terms
                SET category = ?, label = ?, normalized = ?, hints = ?, red_flag = ?, updated_at = ?
                WHERE id = ?
            """, (body.type, body.term, normalized, body.hints, body.red_flag, now, term_id))

            conn.commit()

            # Return updated term
            cursor.execute(
                "SELECT id, category as type, label as term, normalized, hints, red_flag, updated_at FROM dictionary_terms WHERE id = ?",
                (term_id,)
            )
            row = cursor.fetchone()

            return TermOut(
                id=row[0],
                type=row[1],
                term=row[2],
                normalized=row[3],
                hints=row[4],
                red_flag=bool(row[5]) if row[5] is not None else None,
                updated_at=row[6]
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error updating dictionary term")
        raise HTTPException(status_code=500, detail="Database error")


@router.delete("/{term_id}")
def delete_term(term_id: int, repo: SQLiteRepository = Depends(get_repository)):
    """
    Delete a dictionary term.
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()

            # Check if term exists
            cursor.execute("SELECT id FROM dictionary_terms WHERE id = ?", (term_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Term not found")

            # Check if term is used in any nodes
            cursor.execute("SELECT COUNT(*) FROM node_terms WHERE term_id = ?", (term_id,))
            usage_count = cursor.fetchone()[0]

            if usage_count > 0:
                # Log usage but allow deletion
                logger.warning(f"Deleting term {term_id} which is used in {usage_count} nodes")

            # Delete term
            cursor.execute("DELETE FROM dictionary_terms WHERE id = ?", (term_id,))
            conn.commit()

            return None  # 204 No Content

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error deleting dictionary term")
        raise HTTPException(status_code=500, detail="Database error")


@router.get("/{term_id}/usage", response_model=List[UsageResponse])
def get_term_usage(
    term_id: int,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get usage information for a dictionary term.
    """
    try:
        with repo._get_connection() as conn:
            cursor = conn.cursor()

            # Check if term exists
            cursor.execute("SELECT id FROM dictionary_terms WHERE id = ?", (term_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Term not found")

            # Get usage information
            cursor.execute("""
                SELECT nt.node_id, n.depth
                FROM node_terms nt
                JOIN nodes n ON nt.node_id = n.id
                WHERE nt.term_id = ?
                ORDER BY n.depth, n.id
                LIMIT ? OFFSET ?
            """, (term_id, limit, offset))

            rows = cursor.fetchall()

            # Build path for each usage
            usage_list = []
            for row in rows:
                node_id, depth = row

                # Build path by walking up from this node
                path_parts = []
                current_id = node_id

                while current_id:
                    cursor.execute("SELECT label, parent_id FROM nodes WHERE id = ?", (current_id,))
                    path_row = cursor.fetchone()
                    if path_row:
                        path_parts.insert(0, path_row[0])
                        current_id = path_row[1]
                    else:
                        break

                path = " → ".join(path_parts)

                usage_list.append(UsageResponse(
                    node_id=node_id,
                    path=path,
                    depth=depth
                ))

            return usage_list

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting term usage")
        raise HTTPException(status_code=500, detail="Database error")


@router.post("/import")
def import_dictionary_terms(
    file: UploadFile = File(...),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Import dictionary terms from CSV or XLSX file.

    Accepts .csv or .xlsx files with headers: type, term, hints, red_flag
    Returns counts of inserted/updated/skipped terms.
    """
    try:
        # Validate file type
        if not file.filename:
            raise HTTPException(status_code=422, detail=[
                {
                    "loc": ["body", "file"],
                    "msg": "No file provided",
                    "type": "value_error.no_file"
                }
            ])

        if not (file.filename.endswith('.csv') or file.filename.endswith('.xlsx')):
            raise HTTPException(status_code=422, detail=[
                {
                    "loc": ["body", "file"],
                    "msg": "File must be .csv or .xlsx",
                    "type": "value_error.invalid_file_type"
                }
            ])

        # Read file content
        content = file.file.read()

        # Parse file based on type
        if file.filename.endswith('.csv'):
            import io
            df = pd.read_csv(io.StringIO(content.decode('utf-8')))
        else:  # .xlsx
            import io
            df = pd.read_excel(io.BytesIO(content))

        # Validate headers
        expected_headers = ['type', 'term']
        received_headers = [col.lower().strip() for col in df.columns]

        # Check for required headers
        missing_headers = []
        for expected in expected_headers:
            if expected not in received_headers:
                missing_headers.append(expected)

        if missing_headers:
            raise HTTPException(status_code=422, detail=[
                {
                    "loc": ["body", "file"],
                    "msg": "CSV schema mismatch",
                    "type": "value_error.csv_schema",
                    "ctx": {
                        "expected": expected_headers,
                        "received": list(df.columns),
                        "missing": missing_headers
                    }
                }
            ])

        # Process terms
        inserted = 0
        updated = 0
        skipped = 0

        with repo._get_connection() as conn:
            cursor = conn.cursor()

            for idx, row in df.iterrows():
                try:
                    # Extract and validate data
                    term_type = str(row.get('type', '')).strip()
                    term_text = str(row.get('term', '')).strip()
                    hints = str(row.get('hints', '')) if 'hints' in df.columns else None
                    red_flag = str(row.get('red_flag', '')).lower() in ['true', '1', 'yes'] if 'red_flag' in df.columns else False

                    # Skip empty terms
                    if not term_text:
                        skipped += 1
                        continue

                    # Validate type
                    if term_type not in ['vital_measurement', 'node_label', 'outcome_template']:
                        skipped += 1
                        continue

                    # Normalize term
                    normalized = _normalize(term_text)

                    # Check if term already exists
                    cursor.execute(
                        "SELECT id FROM dictionary_terms WHERE category = ? AND normalized = ?",
                        (term_type, normalized)
                    )
                    existing = cursor.fetchone()

                    if existing:
                        # Update existing term
                        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                        cursor.execute("""
                            UPDATE dictionary_terms
                            SET label = ?, hints = ?, red_flag = ?, updated_at = ?
                            WHERE id = ?
                        """, (
                            term_text,
                            hints,
                            red_flag,
                            now,
                            existing[0]
                        ))
                        updated += 1
                    else:
                        # Insert new term
                        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                        cursor.execute("""
                            INSERT INTO dictionary_terms (category, label, normalized, hints, red_flag, updated_at, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            term_type,
                            term_text,
                            normalized,
                            hints,
                            red_flag,
                            now,
                            now
                        ))
                        inserted += 1

                except Exception as e:
                    logger.warning(f"Error processing row {idx}: {e}")
                    skipped += 1
                    continue

            conn.commit()

        return {
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error importing dictionary terms")
        raise HTTPException(status_code=500, detail="Import failed")


@router.get("/normalize")
def normalize_term(
    type: DictType,
    term: str,
    repo: SQLiteRepository = Depends(get_repository)
):
    """Normalize a term for the given type."""
    try:
        normalized = _normalize(term)

        # Check if this normalized term already exists in the dictionary
        with repo._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT normalized FROM dictionary_terms WHERE category = ? AND normalized = ? LIMIT 1",
                (type, normalized)
            )
            row = cursor.fetchone()

            # Return existing normalized term if found, otherwise return computed normalized term
            return {"normalized": row[0] if row else normalized}

        except Exception as e:
        logger.exception("Error normalizing term")
        raise HTTPException(status_code=500, detail="Database error")

