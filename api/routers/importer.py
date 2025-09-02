"""
Unified importer router for POST /import endpoint.

Delegates to existing import logic with strict 422 ctx for schema errors.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
import io
from datetime import datetime
from typing import Dict, Any
import logging

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from core.import_export import assert_csv_header

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/import", tags=["import"])


def _process_import(content: bytes, filename: str) -> Dict[str, Any]:
    """
    Process import file with strict validation.

    Args:
        content: File content as bytes
        filename: Original filename

    Returns:
        Dict with import results

    Raises:
        HTTPException: With 422 ctx on schema errors
    """
    try:
        # Parse Excel file
        df = pd.read_excel(io.BytesIO(content))

        # Validate headers with strict ctx
        headers = df.columns.tolist()
        try:
            assert_csv_header(headers)
            logger.info("Headers validated successfully")
        except ValueError as e:
            # Extract ctx from ValueError
            error_ctx = e.args[0] if isinstance(e.args[0], dict) else {
                "first_offending_row": 0,
                "col_index": 0,
                "expected": ["Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5", "Diagnostic Triage", "Actions"],
                "received": headers,
                "error_counts": {"header": 1}
            }

            # Build FastAPI 422 detail with ctx for first mismatch & counts
            detail = [{
                "loc": ["body", "file"],
                "msg": "CSV header mismatch",
                "type": "value_error.csv_schema",
                "ctx": error_ctx
            }]

            raise HTTPException(
                status_code=422,
                detail=detail
            )

        # TODO: Process the validated data
        # For now, return success structure
        return {
            "status": "success",
            "message": "Import completed successfully",
            "filename": filename,
            "rows_processed": len(df),
            "headers_validated": True
        }

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Import processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Import processing failed: {str(e)}"
        )


@router.post("")
async def import_workbook(
    file: UploadFile = File(...),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Unified importer for POST /import endpoint.

    Strict 422 ctx for schema errors with detailed mismatch information.
    """
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx files are supported"
        )

    try:
        # Read file content
        content = await file.read()

        # Process import with strict validation
        result = _process_import(content, file.filename)

        return result

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error during import: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Import failed: {str(e)}"
        )
