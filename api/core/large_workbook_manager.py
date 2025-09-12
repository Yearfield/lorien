"""
Large Workbook Management System.

Provides efficient handling of large Excel workbooks with chunking,
progress tracking, resume capability, and memory optimization.
"""

import sqlite3
import pandas as pd
import io
import json
import logging
from typing import Dict, Any, List, Optional, Generator, Tuple
from datetime import datetime, timezone
from enum import Enum
import uuid
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class ImportStatus(Enum):
    """Import job statuses."""
    PENDING = "pending"
    PROCESSING = "processing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ChunkStrategy(Enum):
    """Chunking strategies for large workbooks."""
    ROW_BASED = "row_based"
    SIZE_BASED = "size_based"
    MEMORY_BASED = "memory_based"

@dataclass
class ImportProgress:
    """Import progress tracking."""
    total_rows: int
    processed_rows: int
    current_chunk: int
    total_chunks: int
    percentage: float
    estimated_remaining: Optional[str] = None
    current_operation: Optional[str] = None

@dataclass
class ChunkResult:
    """Result of processing a chunk."""
    rows_processed: int
    created_roots: int
    created_nodes: int
    updated_nodes: int
    updated_outcomes: int
    errors: List[str]
    warnings: List[str]

class LargeWorkbookManager:
    """Manages large workbook imports with chunking and progress tracking."""
    
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Ensure required tables exist."""
        cursor = self.conn.cursor()
        
        # Import jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS large_import_jobs (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                total_rows INTEGER NOT NULL,
                chunk_size INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                progress_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                started_at DATETIME,
                completed_at DATETIME,
                error_message TEXT,
                metadata TEXT
            )
        """)
        
        # Import chunks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS large_import_chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                start_row INTEGER NOT NULL,
                end_row INTEGER NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                processed_at DATETIME,
                result_data TEXT,
                error_message TEXT,
                FOREIGN KEY (job_id) REFERENCES large_import_jobs(id) ON DELETE CASCADE
            )
        """)
        
        # Performance monitoring table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS large_import_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL,
                chunk_index INTEGER,
                operation TEXT NOT NULL,
                duration_ms INTEGER NOT NULL,
                memory_mb REAL,
                rows_processed INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES large_import_jobs(id) ON DELETE CASCADE
            )
        """)
        
        # Indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_large_import_jobs_status 
            ON large_import_jobs(status)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_large_import_chunks_job_id 
            ON large_import_chunks(job_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_large_import_chunks_status 
            ON large_import_chunks(status)
        """)
        
        self.conn.commit()
    
    def create_import_job(
        self,
        filename: str,
        total_rows: int,
        chunk_size: int = 1000,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a new large import job."""
        job_id = str(uuid.uuid4())
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT INTO large_import_jobs 
            (id, filename, total_rows, chunk_size, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            job_id,
            filename,
            total_rows,
            chunk_size,
            json.dumps(metadata or {})
        ))
        
        self.conn.commit()
        logger.info(f"Created large import job {job_id} for {filename} with {total_rows} rows")
        return job_id
    
    def get_import_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get import job details."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, filename, total_rows, chunk_size, status, progress_data,
                   created_at, started_at, completed_at, error_message, metadata
            FROM large_import_jobs
            WHERE id = ?
        """, (job_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            "id": row[0],
            "filename": row[1],
            "total_rows": row[2],
            "chunk_size": row[3],
            "status": row[4],
            "progress_data": json.loads(row[5]) if row[5] else {},
            "created_at": row[6],
            "started_at": row[7],
            "completed_at": row[8],
            "error_message": row[9],
            "metadata": json.loads(row[10]) if row[10] else {}
        }
    
    def update_job_status(
        self,
        job_id: str,
        status: ImportStatus,
        progress_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """Update job status and progress."""
        cursor = self.conn.cursor()
        
        update_fields = ["status = ?"]
        params = [status.value]
        
        if progress_data is not None:
            update_fields.append("progress_data = ?")
            params.append(json.dumps(progress_data))
        
        if error_message is not None:
            update_fields.append("error_message = ?")
            params.append(error_message)
        
        if status == ImportStatus.PROCESSING and not self._get_job_field(job_id, "started_at"):
            update_fields.append("started_at = CURRENT_TIMESTAMP")
        elif status in [ImportStatus.COMPLETED, ImportStatus.FAILED, ImportStatus.CANCELLED]:
            update_fields.append("completed_at = CURRENT_TIMESTAMP")
        
        params.append(job_id)
        
        cursor.execute(f"""
            UPDATE large_import_jobs
            SET {', '.join(update_fields)}
            WHERE id = ?
        """, params)
        
        self.conn.commit()
    
    def _get_job_field(self, job_id: str, field: str) -> Any:
        """Get a specific field from a job."""
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT {field} FROM large_import_jobs WHERE id = ?", (job_id,))
        result = cursor.fetchone()
        return result[0] if result else None
    
    def create_chunks(self, job_id: str, total_rows: int, chunk_size: int) -> List[int]:
        """Create chunks for the import job."""
        cursor = self.conn.cursor()
        
        chunks = []
        for i in range(0, total_rows, chunk_size):
            start_row = i
            end_row = min(i + chunk_size - 1, total_rows - 1)
            
            cursor.execute("""
                INSERT INTO large_import_chunks 
                (job_id, chunk_index, start_row, end_row)
                VALUES (?, ?, ?, ?)
            """, (job_id, len(chunks), start_row, end_row))
            
            chunks.append(cursor.lastrowid)
        
        self.conn.commit()
        logger.info(f"Created {len(chunks)} chunks for job {job_id}")
        return chunks
    
    def get_pending_chunks(self, job_id: str) -> List[Dict[str, Any]]:
        """Get pending chunks for a job."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, chunk_index, start_row, end_row, status
            FROM large_import_chunks
            WHERE job_id = ? AND status = 'pending'
            ORDER BY chunk_index
        """, (job_id,))
        
        chunks = []
        for row in cursor.fetchall():
            chunks.append({
                "id": row[0],
                "chunk_index": row[1],
                "start_row": row[2],
                "end_row": row[3],
                "status": row[4]
            })
        
        return chunks
    
    def process_chunk(
        self,
        job_id: str,
        chunk_id: int,
        chunk_data: pd.DataFrame,
        strategy: ChunkStrategy = ChunkStrategy.ROW_BASED
    ) -> ChunkResult:
        """Process a single chunk of data."""
        start_time = datetime.now()
        
        try:
            # Mark chunk as processing
            self._update_chunk_status(chunk_id, "processing")
            
            # Process the chunk
            result = self._process_chunk_data(chunk_data)
            
            # Mark chunk as completed
            self._update_chunk_status(
                chunk_id, 
                "completed", 
                result_data=result.__dict__
            )
            
            # Record performance metrics
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self._record_performance(job_id, chunk_id, "process_chunk", duration_ms, len(chunk_data))
            
            return result
            
        except Exception as e:
            # Mark chunk as failed
            self._update_chunk_status(chunk_id, "failed", error_message=str(e))
            logger.error(f"Chunk {chunk_id} processing failed: {e}")
            raise
    
    def _process_chunk_data(self, chunk_data: pd.DataFrame) -> ChunkResult:
        """Process chunk data and return results."""
        created_roots = 0
        created_nodes = 0
        updated_nodes = 0
        updated_outcomes = 0
        errors = []
        warnings = []
        
        cursor = self.conn.cursor()
        
        for index, row in chunk_data.iterrows():
            try:
                # Get row data
                vm_label = str(row["Vital Measurement"]).strip()
                node_labels = [str(row[f"Node {i}"]).strip() for i in range(1, 6)]
                diagnosis = str(row["Diagnostic Triage"]).strip() if pd.notna(row["Diagnostic Triage"]) else ""
                actions = str(row["Actions"]).strip() if pd.notna(row["Actions"]) else ""
                
                # Skip empty rows
                if not vm_label or vm_label.lower() in ['', 'nan', 'none']:
                    continue
                
                # Process the row
                row_result = self._process_single_row(
                    cursor, vm_label, node_labels, diagnosis, actions
                )
                
                created_roots += row_result["created_roots"]
                created_nodes += row_result["created_nodes"]
                updated_nodes += row_result["updated_nodes"]
                updated_outcomes += row_result["updated_outcomes"]
                
                if row_result.get("warnings"):
                    warnings.extend(row_result["warnings"])
                
            except Exception as e:
                error_msg = f"Row {index + 1}: {str(e)}"
                errors.append(error_msg)
                logger.warning(error_msg)
        
        return ChunkResult(
            rows_processed=len(chunk_data),
            created_roots=created_roots,
            created_nodes=created_nodes,
            updated_nodes=updated_nodes,
            updated_outcomes=updated_outcomes,
            errors=errors,
            warnings=warnings
        )
    
    def _process_single_row(
        self,
        cursor: sqlite3.Cursor,
        vm_label: str,
        node_labels: List[str],
        diagnosis: str,
        actions: str
    ) -> Dict[str, Any]:
        """Process a single row of data."""
        result = {
            "created_roots": 0,
            "created_nodes": 0,
            "updated_nodes": 0,
            "updated_outcomes": 0,
            "warnings": []
        }
        
        # 1. Upsert root VM by label (depth=0)
        cursor.execute("""
            SELECT id FROM nodes 
            WHERE depth = 0 AND LOWER(label) = LOWER(?)
        """, (vm_label,))
        
        root_result = cursor.fetchone()
        if root_result:
            root_id = root_result[0]
        else:
            cursor.execute("""
                INSERT INTO nodes (parent_id, depth, slot, label, is_leaf)
                VALUES (NULL, 0, 0, ?, 0)
            """, (vm_label,))
            root_id = cursor.lastrowid
            result["created_roots"] = 1
        
        # 2. For Node 1..5: create/upsert under correct parent with slots 1..5
        for slot, node_label in enumerate(node_labels, 1):
            if not node_label or node_label.lower() in ['', 'nan', 'none']:
                continue
            
            # Check if node already exists at this slot
            cursor.execute("""
                SELECT id FROM nodes 
                WHERE parent_id = ? AND slot = ?
            """, (root_id, slot))
            
            node_result = cursor.fetchone()
            if node_result:
                # Update existing node
                cursor.execute("""
                    UPDATE nodes SET label = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (node_label, node_result[0]))
                result["updated_nodes"] += 1
            else:
                # Create new node
                cursor.execute("""
                    INSERT INTO nodes (parent_id, depth, slot, label, is_leaf)
                    VALUES (?, 1, ?, ?, 0)
                """, (root_id, slot, node_label))
                result["created_nodes"] += 1
        
        # 3. For the leaf: upsert triage/actions
        leaf_id = self._ensure_leaf_path(cursor, root_id, node_labels)
        
        if leaf_id and (diagnosis or actions):
            # Upsert triage data
            cursor.execute("""
                INSERT OR REPLACE INTO triage (node_id, diagnostic_triage, actions, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (leaf_id, diagnosis, actions))
            result["updated_outcomes"] = 1
        
        return result
    
    def _ensure_leaf_path(self, cursor: sqlite3.Cursor, root_id: int, node_labels: List[str]) -> int:
        """Ensure a complete path exists from root to leaf (depth 5)."""
        current_id = root_id
        current_depth = 0
        
        for slot, node_label in enumerate(node_labels, 1):
            if not node_label or node_label.lower() in ['', 'nan', 'none']:
                node_label = f"Slot {slot}"
            
            current_depth += 1
            
            # Check if child exists at this depth
            cursor.execute("""
                SELECT id FROM nodes 
                WHERE parent_id = ? AND depth = ? AND slot = ?
            """, (current_id, current_depth, slot))
            
            child_result = cursor.fetchone()
            if child_result:
                current_id = child_result[0]
            else:
                # Create child node
                is_leaf = 1 if current_depth == 5 else 0
                cursor.execute("""
                    INSERT INTO nodes (parent_id, depth, slot, label, is_leaf)
                    VALUES (?, ?, ?, ?, ?)
                """, (current_id, current_depth, slot, node_label, is_leaf))
                current_id = cursor.lastrowid
        
        return current_id
    
    def _update_chunk_status(
        self,
        chunk_id: int,
        status: str,
        result_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """Update chunk status."""
        cursor = self.conn.cursor()
        
        update_fields = ["status = ?"]
        params = [status]
        
        if result_data is not None:
            update_fields.append("result_data = ?")
            params.append(json.dumps(result_data))
        
        if error_message is not None:
            update_fields.append("error_message = ?")
            params.append(error_message)
        
        if status == "completed":
            update_fields.append("processed_at = CURRENT_TIMESTAMP")
        
        params.append(chunk_id)
        
        cursor.execute(f"""
            UPDATE large_import_chunks
            SET {', '.join(update_fields)}
            WHERE id = ?
        """, params)
        
        self.conn.commit()
    
    def _record_performance(
        self,
        job_id: str,
        chunk_id: int,
        operation: str,
        duration_ms: int,
        rows_processed: int
    ):
        """Record performance metrics."""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO large_import_performance
            (job_id, chunk_index, operation, duration_ms, rows_processed)
            VALUES (?, ?, ?, ?, ?)
        """, (job_id, chunk_id, operation, duration_ms, rows_processed))
        self.conn.commit()
    
    def get_job_progress(self, job_id: str) -> ImportProgress:
        """Get current progress for a job."""
        cursor = self.conn.cursor()
        
        # Get job details
        job = self.get_import_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # Get chunk statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_chunks,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_chunks,
                COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_chunks
            FROM large_import_chunks
            WHERE job_id = ?
        """, (job_id,))
        
        stats = cursor.fetchone()
        total_chunks, completed_chunks, failed_chunks, processing_chunks = stats
        
        # Calculate progress
        processed_rows = (completed_chunks * job["chunk_size"])
        percentage = (completed_chunks / total_chunks * 100) if total_chunks > 0 else 0
        
        # Estimate remaining time
        estimated_remaining = None
        if completed_chunks > 0 and processing_chunks == 0:
            # Get average processing time
            cursor.execute("""
                SELECT AVG(duration_ms) as avg_duration
                FROM large_import_performance
                WHERE job_id = ? AND operation = 'process_chunk'
            """, (job_id,))
            
            avg_duration = cursor.fetchone()[0]
            if avg_duration:
                remaining_chunks = total_chunks - completed_chunks
                remaining_ms = remaining_chunks * avg_duration
                estimated_remaining = f"{remaining_ms / 1000:.1f}s"
        
        return ImportProgress(
            total_rows=job["total_rows"],
            processed_rows=processed_rows,
            current_chunk=completed_chunks + processing_chunks,
            total_chunks=total_chunks,
            percentage=percentage,
            estimated_remaining=estimated_remaining,
            current_operation="processing" if processing_chunks > 0 else "idle"
        )
    
    def get_job_statistics(self, job_id: str) -> Dict[str, Any]:
        """Get detailed statistics for a job."""
        cursor = self.conn.cursor()
        
        # Get chunk statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_chunks,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_chunks,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_chunks,
                COUNT(CASE WHEN status = 'processing' THEN 1 END) as processing_chunks,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_chunks
            FROM large_import_chunks
            WHERE job_id = ?
        """, (job_id,))
        
        chunk_stats = cursor.fetchone()
        
        # Get performance statistics
        cursor.execute("""
            SELECT 
                AVG(duration_ms) as avg_duration_ms,
                MIN(duration_ms) as min_duration_ms,
                MAX(duration_ms) as max_duration_ms,
                SUM(rows_processed) as total_rows_processed
            FROM large_import_performance
            WHERE job_id = ? AND operation = 'process_chunk'
        """, (job_id,))
        
        perf_stats = cursor.fetchone()
        
        return {
            "chunk_statistics": {
                "total_chunks": chunk_stats[0],
                "completed_chunks": chunk_stats[1],
                "failed_chunks": chunk_stats[2],
                "processing_chunks": chunk_stats[3],
                "pending_chunks": chunk_stats[4]
            },
            "performance_statistics": {
                "avg_duration_ms": perf_stats[0] or 0,
                "min_duration_ms": perf_stats[1] or 0,
                "max_duration_ms": perf_stats[2] or 0,
                "total_rows_processed": perf_stats[3] or 0
            }
        }
    
    def list_import_jobs(
        self,
        status: Optional[ImportStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List import jobs with optional filtering."""
        cursor = self.conn.cursor()
        
        query = """
            SELECT id, filename, total_rows, chunk_size, status, created_at, 
                   started_at, completed_at, error_message
            FROM large_import_jobs
        """
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status.value)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        jobs = []
        for row in rows:
            jobs.append({
                "id": row[0],
                "filename": row[1],
                "total_rows": row[2],
                "chunk_size": row[3],
                "status": row[4],
                "created_at": row[5],
                "started_at": row[6],
                "completed_at": row[7],
                "error_message": row[8]
            })
        
        return jobs
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job."""
        cursor = self.conn.cursor()
        
        # Update job status
        cursor.execute("""
            UPDATE large_import_jobs
            SET status = ?, completed_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status IN ('pending', 'processing')
        """, (ImportStatus.CANCELLED.value, job_id))
        
        if cursor.rowcount == 0:
            return False
        
        # Update pending chunks
        cursor.execute("""
            UPDATE large_import_chunks
            SET status = 'cancelled'
            WHERE job_id = ? AND status = 'pending'
        """, (job_id,))
        
        self.conn.commit()
        logger.info(f"Cancelled import job {job_id}")
        return True
    
    def resume_job(self, job_id: str) -> bool:
        """Resume a paused or failed job."""
        cursor = self.conn.cursor()
        
        # Check if job can be resumed
        cursor.execute("""
            SELECT status FROM large_import_jobs
            WHERE id = ?
        """, (job_id,))
        
        result = cursor.fetchone()
        if not result or result[0] not in ['paused', 'failed']:
            return False
        
        # Update job status
        cursor.execute("""
            UPDATE large_import_jobs
            SET status = ?, started_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (ImportStatus.PROCESSING.value, job_id))
        
        # Reset failed chunks to pending
        cursor.execute("""
            UPDATE large_import_chunks
            SET status = 'pending', error_message = NULL
            WHERE job_id = ? AND status = 'failed'
        """, (job_id,))
        
        self.conn.commit()
        logger.info(f"Resumed import job {job_id}")
        return True
