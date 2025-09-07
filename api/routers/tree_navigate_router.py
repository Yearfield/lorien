from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from typing import Optional, List
from api.db import get_conn, ensure_schema
from api.repositories.tree_repo import root_options, navigate_path

router = APIRouter()

@router.get("/tree/root-options")
def get_root_options():
    conn = get_conn()
    ensure_schema(conn)
    return JSONResponse({"items": root_options(conn)})

@router.get("/tree/navigate")
def get_navigate(root: str, n1: Optional[str] = None, n2: Optional[str] = None,
                 n3: Optional[str] = None, n4: Optional[str] = None, n5: Optional[str] = None,
                 q: Optional[str] = Query(None, description="server-side filter for next-step options")):
    conn = get_conn()
    ensure_schema(conn)
    path = [p for p in [root, n1, n2, n3, n4, n5] if p]
    result = navigate_path(conn, path)
    
    # Apply search filter if provided
    if q and result.get("options"):
        filtered_options = []
        search_term = q.lower()
        for option in result["options"]:
            if search_term in option["label"].lower():
                filtered_options.append(option)
        result["options"] = filtered_options
    
    return JSONResponse(result)
