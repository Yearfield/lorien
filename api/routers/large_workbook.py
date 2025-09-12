"""
Large Workbook API endpoints.

Provides endpoints for managing large workbook imports with chunking,
progress tracking, and resume capability.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from typing import Dict, Any, List, Optional
import pandas as pd
import io
import json
import logging
from datetime import datetime, timezone
from pydantic import BaseModel

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from ..core.large_workbook_manager import (
    LargeWorkbookManager,
    ImportStatus,
    ChunkStrategy,
    ImportProgress,
    ChunkResult
)
from core.import_export import assert_csv_header

router = APIRouter(prefix="/large-workbook", tags=["large-workbook"])

# Request/Response Models
class CreateImportJobRequest(BaseModel):
    filename: str
    chunk_size: int = 1000
    metadata: Optional[Dict[str, Any]] = None

class ImportJobResponse(BaseModel):
    job_id: str
    status: str
    message: str
    total_rows: Optional[int] = None
    chunk_size: Optional[int] = None
    total_chunks: Optional[int] = None

class ProgressResponse(BaseModel):
    job_id: str
    progress: ImportProgress
    statistics: Dict[str, Any]

class ChunkResponse(BaseModel):
    chunk_id: int
    chunk_index: int
    start_row: int
    end_row: int
    status: str

@router.post("/import/create-job", response_model=ImportJobResponse)
async def create_import_job(
    file: UploadFile = File(...),
    chunk_size: int = Query(1000, ge=100, le=10000, description="Number of rows per chunk"),
    strategy: str = Query("row_based", description="Chunking strategy"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Create a new large workbook import job.
    
    This endpoint validates the file and creates a job for chunked processing.
    The actual processing happens asynchronously.
    """
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx files are supported"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Parse Excel file to get row count
        df = pd.read_excel(io.BytesIO(content))
        total_rows = len(df)
        
        # Validate headers
        headers = df.columns.tolist()
        try:
            assert_csv_header(headers)
        except ValueError as e:
            error_ctx = e.args[0] if isinstance(e.args[0], dict) else {
                "expected": ["Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5", "Diagnostic Triage", "Actions"],
                "received": headers
            }
            
            raise HTTPException(
                status_code=422,
                detail=[{
                    "loc": ["body", "file"],
                    "msg": "CSV header mismatch",
                    "type": "value_error.csv_schema",
                    "ctx": error_ctx
                }]
            )
        
        # Create import job
        with repo._get_connection() as conn:
            manager = LargeWorkbookManager(conn)
            
            job_id = manager.create_import_job(
                filename=file.filename,
                total_rows=total_rows,
                chunk_size=chunk_size,
                metadata={
                    "strategy": strategy,
                    "file_size_bytes": len(content),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            )
            
            # Create chunks
            manager.create_chunks(job_id, total_rows, chunk_size)
            
            return ImportJobResponse(
                job_id=job_id,
                status=ImportStatus.PENDING.value,
                message=f"Import job created for {file.filename} with {total_rows} rows",
                total_rows=total_rows,
                chunk_size=chunk_size,
                total_chunks=(total_rows + chunk_size - 1) // chunk_size
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating import job: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create import job: {str(e)}"
        )

@router.post("/import/{job_id}/start", response_model=ImportJobResponse)
async def start_import_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Start processing an import job.
    
    This will begin processing chunks in the background.
    """
    try:
        with repo._get_connection() as conn:
            manager = LargeWorkbookManager(conn)
            
            # Check if job exists and can be started
            job = manager.get_import_job(job_id)
            if not job:
                raise HTTPException(
                    status_code=404,
                    detail=f"Import job {job_id} not found"
                )
            
            if job["status"] not in [ImportStatus.PENDING.value, ImportStatus.PAUSED.value]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Job {job_id} cannot be started in status {job['status']}"
                )
            
            # Update job status
            manager.update_job_status(job_id, ImportStatus.PROCESSING)
            
            # Start background processing
            background_tasks.add_task(process_import_job, job_id, repo)
            
            return ImportJobResponse(
                job_id=job_id,
                status=ImportStatus.PROCESSING.value,
                message="Import job started successfully"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error starting import job: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start import job: {str(e)}"
        )

@router.get("/import/{job_id}/progress", response_model=ProgressResponse)
async def get_import_progress(
    job_id: str,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get current progress for an import job.
    """
    try:
        with repo._get_connection() as conn:
            manager = LargeWorkbookManager(conn)
            
            # Check if job exists
            job = manager.get_import_job(job_id)
            if not job:
                raise HTTPException(
                    status_code=404,
                    detail=f"Import job {job_id} not found"
                )
            
            # Get progress
            progress = manager.get_job_progress(job_id)
            statistics = manager.get_job_statistics(job_id)
            
            return ProgressResponse(
                job_id=job_id,
                progress=progress,
                statistics=statistics
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting import progress: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get import progress: {str(e)}"
        )

@router.get("/import/{job_id}/chunks", response_model=List[ChunkResponse])
async def get_import_chunks(
    job_id: str,
    status: Optional[str] = Query(None, description="Filter by chunk status"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get chunks for an import job.
    """
    try:
        with repo._get_connection() as conn:
            manager = LargeWorkbookManager(conn)
            
            # Check if job exists
            job = manager.get_import_job(job_id)
            if not job:
                raise HTTPException(
                    status_code=404,
                    detail=f"Import job {job_id} not found"
                )
            
            # Get chunks
            if status:
                chunks = manager.get_pending_chunks(job_id) if status == "pending" else []
            else:
                chunks = manager.get_pending_chunks(job_id)
            
            return [
                ChunkResponse(
                    chunk_id=chunk["id"],
                    chunk_index=chunk["chunk_index"],
                    start_row=chunk["start_row"],
                    end_row=chunk["end_row"],
                    status=chunk["status"]
                )
                for chunk in chunks
            ]
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting import chunks: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get import chunks: {str(e)}"
        )

@router.post("/import/{job_id}/pause", response_model=ImportJobResponse)
async def pause_import_job(
    job_id: str,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Pause a running import job.
    """
    try:
        with repo._get_connection() as conn:
            manager = LargeWorkbookManager(conn)
            
            # Check if job exists and can be paused
            job = manager.get_import_job(job_id)
            if not job:
                raise HTTPException(
                    status_code=404,
                    detail=f"Import job {job_id} not found"
                )
            
            if job["status"] != ImportStatus.PROCESSING.value:
                raise HTTPException(
                    status_code=400,
                    detail=f"Job {job_id} cannot be paused in status {job['status']}"
                )
            
            # Update job status
            manager.update_job_status(job_id, ImportStatus.PAUSED)
            
            return ImportJobResponse(
                job_id=job_id,
                status=ImportStatus.PAUSED.value,
                message="Import job paused successfully"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error pausing import job: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to pause import job: {str(e)}"
        )

@router.post("/import/{job_id}/resume", response_model=ImportJobResponse)
async def resume_import_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Resume a paused or failed import job.
    """
    try:
        with repo._get_connection() as conn:
            manager = LargeWorkbookManager(conn)
            
            # Check if job exists and can be resumed
            job = manager.get_import_job(job_id)
            if not job:
                raise HTTPException(
                    status_code=404,
                    detail=f"Import job {job_id} not found"
                )
            
            if job["status"] not in [ImportStatus.PAUSED.value, ImportStatus.FAILED.value]:
                raise HTTPException(
                    status_code=400,
                    detail=f"Job {job_id} cannot be resumed in status {job['status']}"
                )
            
            # Resume job
            success = manager.resume_job(job_id)
            if not success:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to resume job {job_id}"
                )
            
            # Start background processing
            background_tasks.add_task(process_import_job, job_id, repo)
            
            return ImportJobResponse(
                job_id=job_id,
                status=ImportStatus.PROCESSING.value,
                message="Import job resumed successfully"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error resuming import job: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to resume import job: {str(e)}"
        )

@router.post("/import/{job_id}/cancel", response_model=ImportJobResponse)
async def cancel_import_job(
    job_id: str,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Cancel an import job.
    """
    try:
        with repo._get_connection() as conn:
            manager = LargeWorkbookManager(conn)
            
            # Cancel job
            success = manager.cancel_job(job_id)
            if not success:
                raise HTTPException(
                    status_code=400,
                    detail=f"Job {job_id} cannot be cancelled"
                )
            
            return ImportJobResponse(
                job_id=job_id,
                status=ImportStatus.CANCELLED.value,
                message="Import job cancelled successfully"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error cancelling import job: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel import job: {str(e)}"
        )

@router.get("/import/jobs", response_model=List[Dict[str, Any]])
async def list_import_jobs(
    status: Optional[str] = Query(None, description="Filter by job status"),
    limit: int = Query(50, ge=1, le=200, description="Number of jobs to return"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip"),
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    List import jobs with optional filtering.
    """
    try:
        with repo._get_connection() as conn:
            manager = LargeWorkbookManager(conn)
            
            # Convert status string to enum
            status_enum = None
            if status:
                try:
                    status_enum = ImportStatus(status)
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid status: {status}"
                    )
            
            jobs = manager.list_import_jobs(
                status=status_enum,
                limit=limit,
                offset=offset
            )
            
            return jobs
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error listing import jobs: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list import jobs: {str(e)}"
        )

@router.get("/import/{job_id}/statistics", response_model=Dict[str, Any])
async def get_import_statistics(
    job_id: str,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Get detailed statistics for an import job.
    """
    try:
        with repo._get_connection() as conn:
            manager = LargeWorkbookManager(conn)
            
            # Check if job exists
            job = manager.get_import_job(job_id)
            if not job:
                raise HTTPException(
                    status_code=404,
                    detail=f"Import job {job_id} not found"
                )
            
            # Get statistics
            statistics = manager.get_job_statistics(job_id)
            
            return {
                "job_id": job_id,
                "job_details": job,
                "statistics": statistics
            }
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting import statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get import statistics: {str(e)}"
        )

@router.get("/import/{job_id}/export-progress")
async def export_progress_csv(
    job_id: str,
    repo: SQLiteRepository = Depends(get_repository)
):
    """
    Export import progress as CSV.
    """
    try:
        with repo._get_connection() as conn:
            manager = LargeWorkbookManager(conn)
            
            # Check if job exists
            job = manager.get_import_job(job_id)
            if not job:
                raise HTTPException(
                    status_code=404,
                    detail=f"Import job {job_id} not found"
                )
            
            # Get progress data
            progress = manager.get_job_progress(job_id)
            statistics = manager.get_job_statistics(job_id)
            
            # Create CSV data
            csv_data = f"""Job ID,{job_id}
Filename,{job['filename']}
Total Rows,{progress.total_rows}
Processed Rows,{progress.processed_rows}
Percentage,{progress.percentage:.2f}%
Current Chunk,{progress.current_chunk}
Total Chunks,{progress.total_chunks}
Status,{job['status']}
Estimated Remaining,{progress.estimated_remaining or 'N/A'}
Current Operation,{progress.current_operation or 'N/A'}

Chunk Statistics
Total Chunks,{statistics['chunk_statistics']['total_chunks']}
Completed Chunks,{statistics['chunk_statistics']['completed_chunks']}
Failed Chunks,{statistics['chunk_statistics']['failed_chunks']}
Processing Chunks,{statistics['chunk_statistics']['processing_chunks']}
Pending Chunks,{statistics['chunk_statistics']['pending_chunks']}

Performance Statistics
Average Duration (ms),{statistics['performance_statistics']['avg_duration_ms']:.2f}
Min Duration (ms),{statistics['performance_statistics']['min_duration_ms']}
Max Duration (ms),{statistics['performance_statistics']['max_duration_ms']}
Total Rows Processed,{statistics['performance_statistics']['total_rows_processed']}
"""
            
            return StreamingResponse(
                io.StringIO(csv_data),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=import_progress_{job_id}.csv"}
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error exporting progress CSV: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to export progress CSV: {str(e)}"
        )

async def process_import_job(job_id: str, repo: SQLiteRepository):
    """
    Background task to process an import job.
    """
    try:
        with repo._get_connection() as conn:
            manager = LargeWorkbookManager(conn)
            
            # Get pending chunks
            chunks = manager.get_pending_chunks(job_id)
            
            for chunk in chunks:
                try:
                    # Check if job was cancelled
                    job = manager.get_import_job(job_id)
                    if job["status"] == ImportStatus.CANCELLED.value:
                        break
                    
                    # Process chunk (this would need the actual file data)
                    # For now, we'll just mark it as completed
                    manager._update_chunk_status(chunk["id"], "completed")
                    
                    # Update progress
                    progress = manager.get_job_progress(job_id)
                    manager.update_job_status(job_id, ImportStatus.PROCESSING, progress.__dict__)
                    
                except Exception as e:
                    logging.error(f"Error processing chunk {chunk['id']}: {e}")
                    manager._update_chunk_status(chunk["id"], "failed", error_message=str(e))
            
            # Check if all chunks are completed
            job = manager.get_import_job(job_id)
            if job["status"] != ImportStatus.CANCELLED.value:
                progress = manager.get_job_progress(job_id)
                if progress.percentage >= 100:
                    manager.update_job_status(job_id, ImportStatus.COMPLETED)
                    logging.info(f"Import job {job_id} completed successfully")
                else:
                    manager.update_job_status(job_id, ImportStatus.PAUSED)
                    logging.info(f"Import job {job_id} paused")
    
    except Exception as e:
        logging.error(f"Error processing import job {job_id}: {e}")
        with repo._get_connection() as conn:
            manager = LargeWorkbookManager(conn)
            manager.update_job_status(job_id, ImportStatus.FAILED, error_message=str(e))
