"""
Dictionary router for medical term administration.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field, constr
from typing import List, Optional, Literal
import sqlite3
import logging
import re
from datetime import datetime, timezone

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


class TermOut(BaseModel):
    id: int
    type: DictType
    term: str
    normalized: str
    hints: Optional[str] = None
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
            sql = "SELECT id, type, term, normalized, hints, updated_at FROM dictionary_terms"
            params = []
            conditions = []

            if type:
                conditions.append("type = ?")
                params.append(type)

            if query:
                # For node_label suggestions, enforce minimum query length
                if type == "node_label" and len(query.strip()) < 2:
                    return []  # Return empty for short queries

                conditions.append("(term LIKE ? OR normalized LIKE ?)")
                like_query = f"%{query}%"
                params.extend([like_query, like_query])

            if conditions:
                sql += " WHERE " + " AND ".join(conditions)

            # Sort options
            if sort == "label":
                sort_field = "term"
            elif sort == "type":
                sort_field = "type"
            else:
                sort_field = "term"

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
                    updated_at=row[5]
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

            # Check for duplicate (type, normalized)
            cursor.execute(
                "SELECT id FROM dictionary_terms WHERE type = ? AND normalized = ?",
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
                INSERT INTO dictionary_terms (type, term, normalized, hints, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (body.type, body.term, normalized, body.hints, now))

            term_id = cursor.lastrowid
            conn.commit()

            # Return created term
            cursor.execute(
                "SELECT id, type, term, normalized, hints, updated_at FROM dictionary_terms WHERE id = ?",
                (term_id,)
            )
            row = cursor.fetchone()

            return TermOut(
                id=row[0],
                type=row[1],
                term=row[2],
                normalized=row[3],
                hints=row[4],
                updated_at=row[5]
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

            # Check for duplicate (type, normalized) (excluding current term)
            cursor.execute(
                "SELECT id FROM dictionary_terms WHERE type = ? AND normalized = ? AND id != ?",
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
                SET type = ?, term = ?, normalized = ?, hints = ?, updated_at = ?
                WHERE id = ?
            """, (body.type, body.term, normalized, body.hints, now, term_id))

            conn.commit()

            # Return updated term
            cursor.execute(
                "SELECT id, type, term, normalized, hints, updated_at FROM dictionary_terms WHERE id = ?",
                (term_id,)
            )
            row = cursor.fetchone()

            return TermOut(
                id=row[0],
                type=row[1],
                term=row[2],
                normalized=row[3],
                hints=row[4],
                updated_at=row[5]
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
                "SELECT normalized FROM dictionary_terms WHERE type = ? AND normalized = ? LIMIT 1",
                (type, normalized)
            )
            row = cursor.fetchone()

            # Return existing normalized term if found, otherwise return computed normalized term
            return {"normalized": row[0] if row else normalized}

    except Exception as e:
        logger.exception("Error normalizing term")
        raise HTTPException(status_code=500, detail="Database error")

