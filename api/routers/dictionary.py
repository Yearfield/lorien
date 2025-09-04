"""
Dictionary router for term normalization and CRUD operations.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, field_validator
from typing import Optional, List, Literal
from storage.sqlite import SQLiteRepository
from api.dependencies import get_repository

DictType = Literal["vital_measurement","node_label","outcome_template"]

router = APIRouter(prefix="/dictionary", tags=["dictionary"])

def _canonical_norm(s: str) -> str:
    # trim, collapse whitespace, lowercase
    return " ".join((s or "").strip().split()).lower()

class DictCreate(BaseModel):
    type: DictType
    term: str
    normalized: Optional[str] = None
    hints: Optional[str] = None
    @field_validator("term")
    @classmethod
    def v_term(cls, v: str) -> str:
        if not v or not v.strip(): raise ValueError("term required")
        return v
    @field_validator("normalized")
    @classmethod
    def v_norm(cls, v: Optional[str], info) -> str:
        # compute if missing
        if v is not None:
            return _canonical_norm(v)
        term = info.data.get("term", "")
        return _canonical_norm(term)

class DictUpdate(BaseModel):
    term: Optional[str] = None
    normalized: Optional[str] = None
    hints: Optional[str] = None
    @field_validator("term")
    @classmethod
    def v_term_opt(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip(): raise ValueError("term cannot be empty")
        return v
    @field_validator("normalized")
    @classmethod
    def v_norm_opt(cls, v: Optional[str], info):
        if v is None:
            term = info.data.get("term")
            return _canonical_norm(term) if term else None
        return _canonical_norm(v)

@router.get("/normalize")
def normalize(type: DictType, term: str, repo: SQLiteRepository = Depends(get_repository)):
    norm = _canonical_norm(term)
    with repo._get_connection() as c:
        row = c.execute("""SELECT normalized FROM dictionary_terms
                           WHERE type=? AND normalized=? LIMIT 1""", (type, norm)).fetchone()
    return {"normalized": row[0] if row else norm}

@router.get("")
def list_terms(type: Optional[DictType] = None, query: str = "", limit: int = 50, offset: int = 0, repo: SQLiteRepository = Depends(get_repository)):
    q = f"%{_canonical_norm(query)}%"
    with repo._get_connection() as c:
        if type:
            rows = c.execute("""
              SELECT id,type,term,normalized,hints,updated_at
              FROM dictionary_terms
              WHERE type=? AND (lower(term) LIKE ? OR normalized LIKE ?)
              ORDER BY updated_at DESC, id DESC
              LIMIT ? OFFSET ?""", (type, q, q, limit, offset)).fetchall()
            total = c.execute("""
              SELECT COUNT(*) FROM dictionary_terms
              WHERE type=? AND (lower(term) LIKE ? OR normalized LIKE ?)""", (type, q, q)).fetchone()[0]
        else:
            rows = c.execute("""
              SELECT id,type,term,normalized,hints,updated_at
              FROM dictionary_terms
              WHERE (lower(term) LIKE ? OR normalized LIKE ?)
              ORDER BY updated_at DESC, id DESC
              LIMIT ? OFFSET ?""", (q, q, limit, offset)).fetchall()
            total = c.execute("""
              SELECT COUNT(*) FROM dictionary_terms
              WHERE (lower(term) LIKE ? OR normalized LIKE ?)""", (q, q)).fetchone()[0]
    items = [dict(id=r[0], type=r[1], term=r[2], normalized=r[3], hints=r[4], updated_at=r[5]) for r in rows]
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.post("")
def create_term(payload: DictCreate, repo: SQLiteRepository = Depends(get_repository)):
    # Ensure normalized is set
    normalized = payload.normalized
    if not normalized:
        normalized = _canonical_norm(payload.term)

    with repo._get_connection() as c:
        try:
            cur = c.cursor()
            cur.execute("""INSERT INTO dictionary_terms(type,term,normalized,hints)
                           VALUES (?,?,?,?)""", (payload.type, payload.term, normalized, payload.hints))
            c.commit()
            rid = cur.lastrowid
            row = cur.execute("""SELECT id,type,term,normalized,hints,updated_at
                                 FROM dictionary_terms WHERE id=?""", (rid,)).fetchone()
            return dict(id=row[0], type=row[1], term=row[2], normalized=row[3], hints=row[4], updated_at=row[5])
        except Exception as e:
            # Check if it's a uniqueness constraint violation
            if "UNIQUE constraint failed" in str(e):
                raise HTTPException(status_code=422, detail=[{"loc":["body","normalized"],"msg":"duplicate normalized term for type","type":"value_error.duplicate"}])
            # Re-raise other exceptions
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}")
def get_term(id: int, repo: SQLiteRepository = Depends(get_repository)):
    with repo._get_connection() as c:
        row = c.execute("""SELECT id,type,term,normalized,hints,updated_at
                           FROM dictionary_terms WHERE id=?""", (id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="term not found")
        return dict(id=row[0], type=row[1], term=row[2], normalized=row[3], hints=row[4], updated_at=row[5])

@router.put("/{id}")
def update_term(id: int, payload: DictUpdate, repo: SQLiteRepository = Depends(get_repository)):
    sets = []; vals = []
    if payload.term is not None: sets.append("term=?"); vals.append(payload.term)
    if payload.normalized is not None: sets.append("normalized=?"); vals.append(payload.normalized)
    if payload.hints is not None: sets.append("hints=?"); vals.append(payload.hints)
    if not sets: return {"ok": True}
    with repo._get_connection() as c:
        try:
            c.execute(f"UPDATE dictionary_terms SET {', '.join(sets)} WHERE id=?", (*vals, id))
            c.commit()
            row = c.execute("""SELECT id,type,term,normalized,hints,updated_at
                               FROM dictionary_terms WHERE id=?""", (id,)).fetchone()
            if not row: raise HTTPException(status_code=404, detail="not found")
            return dict(id=row[0], type=row[1], term=row[2], normalized=row[3], hints=row[4], updated_at=row[5])
        except Exception as e:
            # Check if it's a uniqueness constraint violation
            if "UNIQUE constraint failed" in str(e):
                raise HTTPException(status_code=422, detail=[{"loc":["body","normalized"],"msg":"duplicate normalized term for type","type":"value_error.duplicate"}])
            # Re-raise other exceptions
            raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{id}")
def delete_term(id: int, repo: SQLiteRepository = Depends(get_repository)):
    with repo._get_connection() as c:
        c.execute("DELETE FROM dictionary_terms WHERE id=?", (id,))
        c.commit()
    return {"ok": True, "id": id}
