"""
Dictionary router for medical term administration.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field, constr
from typing import List, Optional, Literal
import sqlite3
import logging
import re
from datetime import datetime, timezone

from api.db import get_conn, ensure_schema

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


class DictionaryListResponse(BaseModel):
    items: List[TermOut]
    total: int
    limit: int
    offset: int


@router.get("", response_model=DictionaryListResponse)
def list_terms(
    type: Optional[DictType] = Query(None, description="Filter by type"),
    query: str = Query("", description="Search query for terms"),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    sort: str = Query("label", description="Sort field"),
    direction: str = Query("asc", description="Sort direction")
):
    """
    List dictionary terms with search, filtering, and pagination.
    """
    try:
        conn = get_conn()
        ensure_schema(conn)
        cursor = conn.cursor()

        # Build query
        sql = "SELECT id, type, term, normalized, hints, updated_at FROM dictionary_terms"
        params = []
        conditions = []

        if type:
            conditions.append("type = ?")
            params.append(type)

        if query:
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

        # Get total count for pagination
        count_sql = "SELECT COUNT(*) FROM dictionary_terms"
        count_params = []
        count_conditions = []
        
        if type:
            count_conditions.append("type = ?")
            count_params.append(type)
        
        if query:
            count_conditions.append("(term LIKE ? OR normalized LIKE ?)")
            like_query = f"%{query}%"
            count_params.extend([like_query, like_query])
        
        if count_conditions:
            count_sql += " WHERE " + " AND ".join(count_conditions)
        
        cursor.execute(count_sql, count_params)
        total = cursor.fetchone()[0]

        items = [
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

        return DictionaryListResponse(
            items=items,
            total=total,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        logger.exception("Error listing dictionary terms")
        raise HTTPException(status_code=500, detail="Database error")


@router.post("", status_code=201, response_model=TermOut)
def create_term(body: TermIn):
    """
    Create a new dictionary term.
    """
    try:
        conn = get_conn()
        ensure_schema(conn)
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
            INSERT INTO dictionary_terms (type, term, normalized, hints, red_flag, updated_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (body.type, body.term, normalized, body.hints, 0, now, now))

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


@router.get("/normalize")
def normalize_term(
    type: DictType,
    term: str
):
    """Normalize a term for the given type."""
    try:
        normalized = _normalize(term)
        return {"normalized": normalized}

    except Exception as e:
        logger.exception("Error normalizing term")
        raise HTTPException(status_code=500, detail="Database error")