from fastapi import APIRouter, Path
from fastapi.responses import JSONResponse
from api.db import get_conn, ensure_schema, tx

router = APIRouter()

@router.delete("/tree/{node_id}")
def delete_parent(node_id: int = Path(..., ge=1)):
    conn = get_conn()
    ensure_schema(conn)
    with tx(conn):
        conn.execute("DELETE FROM nodes WHERE id=?", (node_id,))
    return JSONResponse({"ok": True, "deleted_id": node_id})
