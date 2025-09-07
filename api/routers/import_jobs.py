"""
Import jobs router for tracking import states and providing structured logging.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import logging
import pandas as pd
import io
from datetime import datetime

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from core.import_export import assert_csv_header

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/import", tags=["import"])


class ImportJobResponse(BaseModel):
    id: int
    state: str
    created_at: str
    finished_at: Optional[str]
    message: Optional[str]
    filename: Optional[str]
    size_bytes: Optional[int]


@router.post("/excel", response_model=ImportJobResponse)
async def import_excel(
    file: UploadFile = File(...),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Import Excel file with job tracking.
    
    Args:
        file: Excel file to import
        repo: Database repository
        
    Returns:
        ImportJobResponse with job details
    """
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx files are supported"
        )
    
    try:
        # Create import job
        job_id = repo.create_import_job(
            state="queued",
            filename=file.filename,
            size_bytes=0  # Will be updated after reading
        )
        
        logger.info(f"Created import job {job_id} for file {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Update job with actual size
        repo.update_import_job(job_id, size_bytes=len(content))
        
        # Update job state to processing
        repo.update_import_job(job_id, state="processing")
        
        try:
            # Parse Excel file
            df = pd.read_excel(io.BytesIO(content))
            
            # Validate headers
            headers = df.columns.tolist()
            try:
                assert_csv_header(headers)
                logger.info(f"Import job {job_id}: Headers validated successfully")
            except ValueError as e:
                # Header validation failed
                error_ctx = e.args[0]
                error_message = f"CSV header mismatch: expected {len(error_ctx['expected'])} columns, got {len(error_ctx['received'])}"
                if 'col_index' in error_ctx:
                    error_message += f"; first mismatch at column {error_ctx['col_index']}"
                
                repo.update_import_job(
                    job_id, 
                    state="failed", 
                    message=error_message,
                    finished_at=datetime.utcnow().isoformat()
                )
                
                logger.error(f"Import job {job_id} failed: {error_message}")
                
                raise HTTPException(
                    status_code=422,
                    detail=[{
                        "loc": ["body", "file"],
                        "msg": "CSV header mismatch",
                        "type": "value_error.csv_schema",
                        "ctx": error_ctx
                    }]
                )
            
            # TODO: Process the validated data
            # For now, just mark as done
            repo.update_import_job(
                job_id,
                state="done",
                message="Import completed successfully",
                finished_at=datetime.utcnow().isoformat()
            )
            
            logger.info(f"Import job {job_id} completed successfully")
            
            return ImportJobResponse(
                id=job_id,
                state="done",
                created_at=repo.get_import_job(job_id)["created_at"],
                finished_at=datetime.utcnow().isoformat(),
                message="Import completed successfully",
                filename=file.filename,
                size_bytes=len(content)
            )
            
        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            # Processing failed
            error_message = f"Processing failed: {str(e)}"
            repo.update_import_job(
                job_id,
                state="failed",
                message=error_message,
                finished_at=datetime.utcnow().isoformat()
            )
            
            logger.error(f"Import job {job_id} failed during processing: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Import processing failed: {str(e)}"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process Excel file: {str(e)}"
        )


@router.get("/jobs", response_model=List[ImportJobResponse])
async def get_import_jobs(
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get all import jobs.
    
    Args:
        repo: Database repository
        
    Returns:
        List of import jobs
    """
    try:
        jobs = repo.get_import_jobs()
        return [ImportJobResponse(**job) for job in jobs]
    except Exception as e:
        logger.error(f"Failed to get import jobs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get import jobs: {str(e)}"
        )


@router.get("/jobs/{job_id:int}", response_model=ImportJobResponse)
async def get_import_job(
    job_id: int,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get specific import job.
    
    Args:
        job_id: Import job ID
        repo: Database repository
        
    Returns:
        Import job details
    """
    try:
        job = repo.get_import_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Import job not found")
        return ImportJobResponse(**job)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get import job {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get import job: {str(e)}"
        )
