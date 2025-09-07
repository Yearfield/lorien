from fastapi import APIRouter, HTTPException, Path
from fastapi import Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, constr
import sqlite3

from api.db import get_conn, ensure_schema
from api.repositories.tree_repo import next_incomplete_parent, put_slot_label

router = APIRouter()

class SlotLabel(BaseModel):
    label: constr(strip_whitespace=True, min_length=1)

@router.get("/tree/next-incomplete-parent-json")
def get_next_incomplete_parent():
    conn = get_conn()
    ensure_schema(conn)
    item = next_incomplete_parent(conn)
    if not item:
        return JSONResponse(status_code=204, content=None)
    return JSONResponse(item)

@router.put("/tree/{parent_id}/slot/{slot}")
def put_child_slot(
    parent_id: int = Path(..., ge=1),
    slot: int = Path(..., ge=1, le=5),
    payload: SlotLabel = Body(...)
):
    conn = get_conn()
    ensure_schema(conn)
    label = payload.label.strip()

    # Manual validations resulting in 422 with FastAPI-style detail
    # parent existence and depth handled in repo via exceptions -> map to 422
    try:
        result = put_slot_label(conn, parent_id, slot, label)
        return JSONResponse(result)
    except LookupError as e:
        raise HTTPException(status_code=422, detail=[{
            "loc": ["path", "parent_id"],
            "msg": "Parent not found",
            "type": "value_error.parent_not_found"
        }])
    except ValueError as e:
        msg = str(e)
        if msg == "slot_out_of_range":
            raise HTTPException(status_code=422, detail=[{
                "loc": ["path", "slot"],
                "msg": "Slot must be between 1 and 5",
                "type": "value_error.slot_range"
            }])
        if msg == "parent_at_max_depth":
            raise HTTPException(status_code=422, detail=[{
                "loc": ["path", "parent_id"],
                "msg": "Parent cannot have children (max depth reached)",
                "type": "value_error.depth_max"
            }])
        raise
    except sqlite3.IntegrityError:
        # Unique constraint hit -> conflict
        raise HTTPException(status_code=409, detail=[{
            "loc": ["path", "slot"],
            "msg": "Slot already occupied (concurrent update)",
            "type": "conflict.slot_unique"
        }])
    except RuntimeError as e:
        if str(e) == "slot_occupied_conflict":
            raise HTTPException(status_code=409, detail=[{
                "loc": ["path", "slot"],
                "msg": "Slot occupied by a different child",
                "type": "conflict.slot_occupied"
            }])
        raise
