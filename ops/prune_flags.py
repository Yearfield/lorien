#!/usr/bin/env python3
"""
Flag audit retention job.
Prunes flag_audit table to keep last 30 days OR 50k rows (whichever first).
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from storage.sqlite import SQLiteRepository

logger = logging.getLogger(__name__)


def prune_flag_audit(db_path: str) -> int:
    """
    Prune flag_audit table based on retention policy.
    
    Args:
        db_path: Path to SQLite database
        
    Returns:
        Number of rows pruned
    """
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get current count
            cursor.execute("SELECT COUNT(*) FROM flag_audit")
            current_count = cursor.fetchone()[0]
            
            logger.info(f"Current flag_audit count: {current_count}")
            
            # Check if we need to prune
            needs_time_prune = False
            needs_count_prune = False
            
            # Check for old records (>30 days)
            cursor.execute("""
                SELECT COUNT(*) FROM flag_audit 
                WHERE ts < datetime('now', '-30 days')
            """)
            old_count = cursor.fetchone()[0]
            
            if old_count > 0:
                needs_time_prune = True
                logger.info(f"Found {old_count} records older than 30 days")
            
            # Check if over 50k records
            if current_count > 50000:
                needs_count_prune = True
                logger.info(f"Current count {current_count} exceeds 50k limit")
            
            if not needs_time_prune and not needs_count_prune:
                logger.info("No pruning needed")
                return 0
            
            # Determine pruning strategy
            if needs_time_prune and needs_count_prune:
                # Prune by time first, then by count if still needed
                cursor.execute("""
                    DELETE FROM flag_audit
                    WHERE ts < datetime('now', '-30 days')
                """)
                time_pruned = cursor.rowcount
                
                # Check if still over 50k after time pruning
                cursor.execute("SELECT COUNT(*) FROM flag_audit")
                remaining_count = cursor.fetchone()[0]
                
                if remaining_count > 50000:
                    # Prune oldest records to get to 50k
                    cursor.execute("""
                        DELETE FROM flag_audit
                        WHERE id IN (
                            SELECT id FROM flag_audit
                            ORDER BY ts ASC, id ASC
                            LIMIT ?
                        )
                    """, (remaining_count - 50000,))
                    count_pruned = cursor.rowcount
                    total_pruned = time_pruned + count_pruned
                    logger.info(f"Pruned {time_pruned} by time, {count_pruned} by count")
                else:
                    total_pruned = time_pruned
                    logger.info(f"Pruned {time_pruned} by time only")
                    
            elif needs_time_prune:
                # Prune by time only
                cursor.execute("""
                    DELETE FROM flag_audit
                    WHERE ts < datetime('now', '-30 days')
                """)
                total_pruned = cursor.rowcount
                logger.info(f"Pruned {total_pruned} records by time")
                
            elif needs_count_prune:
                # Prune by count only
                cursor.execute("""
                    DELETE FROM flag_audit
                    WHERE id IN (
                        SELECT id FROM flag_audit
                        ORDER BY ts ASC, id ASC
                        LIMIT ?
                    )
                """, (current_count - 50000,))
                total_pruned = cursor.rowcount
                logger.info(f"Pruned {total_pruned} records by count")
            
            conn.commit()
            
            # Get final count
            cursor.execute("SELECT COUNT(*) FROM flag_audit")
            final_count = cursor.fetchone()[0]
            
            logger.info(f"Pruning complete: {total_pruned} rows removed, {final_count} remaining")
            
            return total_pruned
            
    except Exception as e:
        logger.error(f"Failed to prune flag_audit: {e}")
        raise


def main():
    """Main entry point for the prune job."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get database path from environment or use default
    db_path = os.getenv("LORIEN_DB_PATH")
    if not db_path:
        # Use default path
        repo = SQLiteRepository()
        db_path = repo.db_path
    
    logger.info(f"Starting flag audit prune job for database: {db_path}")
    
    try:
        pruned_count = prune_flag_audit(db_path)
        logger.info(f"Prune job completed successfully: {pruned_count} rows pruned")
        return 0
        
    except Exception as e:
        logger.error(f"Prune job failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
