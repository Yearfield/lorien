from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
from fastapi.responses import JSONResponse

from api.dependencies import get_db_connection
from Engines.EngineLongBow import ingest_file, apply_import, apply_import_with_metadata, FROZEN_HEADER
import sqlite3

router = APIRouter()


@router.post("/import/preview")
async def import_preview(file: UploadFile = File(...)):
    """Preview import without writing to database - shows detected paths."""
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "file"], "msg": f"Could not read file: {str(e)}", "type":"value_error.file_read"}]
        )
    
    # Use EngineLongBow to ingest file
    ingest_result = ingest_file(file_content, file.filename)
    
    if not ingest_result["success"]:
        raise HTTPException(
            status_code=422,
            detail=[ingest_result["error"]]
        )
    
    # Extract unique root labels (D0) from paths
    roots = []
    for path_with_meta in ingest_result["paths"]:
        path = path_with_meta['path']
        if path and len(path) > 0:
            roots.append(path[0])
    
    uniq = sorted(set(roots))
    
    return JSONResponse({
        "ok": True, 
        "rows": ingest_result["total_rows"], 
        "valid_rows": ingest_result["valid_rows"],
        "roots_detected": uniq, 
        "roots_count": len(uniq)
    })

@router.post("/import")
async def import_file(
    file: UploadFile = File(...), 
    mode: str = Query("append", pattern="^(append|replace|hard_replace)$"), 
    conn: sqlite3.Connection = Depends(get_db_connection)
):
    # Read file content
    try:
        file_content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", "file"], "msg": f"Could not read file: {str(e)}", "type":"value_error.file_read"}]
        )

    # Use EngineLongBow to ingest file
    ingest_result = ingest_file(file_content, file.filename)
    
    if not ingest_result["success"]:
        raise HTTPException(
            status_code=422,
            detail=[ingest_result["error"]]
        )

    # Apply import using EngineLongBow
    try:
        # Map mode to EngineLongBow mode
        engine_mode = "replace" if mode in ["replace", "hard_replace"] else "append"
        
        # Apply import with metadata support using the provided connection
        import_result = apply_import_with_metadata(ingest_result["paths"], engine_mode, conn)
        
        return JSONResponse({
            "ok": True,
            "rows": ingest_result["total_rows"],
            "mode": mode,
            "result": {
                "status": "success",
                "rows_processed": ingest_result["valid_rows"],
                "created": {
                    "roots": 0,  # EngineLongBow doesn't track roots separately
                    "nodes": import_result.inserted_nodes
                },
                "updated": {
                    "nodes": 0
                },
                "skipped": {
                    "overfull_parents": 0  # EngineLongBow doesn't enforce 5-child limit
                }
            }
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=[{"loc": ["body"], "msg": f"Import failed: {str(e)}", "type":"value_error.import_failed"}]
        )
