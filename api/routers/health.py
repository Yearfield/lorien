"""
Health check router for the decision tree API.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any
import os

from ..dependencies import get_repository
from storage.sqlite import SQLiteRepository
from core.version import __version__

router = APIRouter(tags=["health"])

# Application version - imported from core.version

@router.get("/health")
async def health_check(repo: SQLiteRepository = Depends(get_repository)) -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    
    Returns:
        JSON with health status, version, database info, and feature flags
    """
    # Check database status
    db_info = await _check_database_health(repo)
    
    # Check feature flags
    features = await _check_features()
    
    return {
        "ok": True,
        "version": __version__,
        "db": db_info,
        "features": features
    }

async def _check_database_health(repo: SQLiteRepository) -> Dict[str, Any]:
    """Check database configuration and health."""
    try:
        with repo._get_connection() as conn:
            # Get database configuration
            cursor = conn.cursor()
            
            # Check WAL mode
            cursor.execute("PRAGMA journal_mode")
            journal_mode = cursor.fetchone()[0]
            
            # Check foreign keys
            cursor.execute("PRAGMA foreign_keys")
            foreign_keys = cursor.fetchone()[0]
            
            # Check page size
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            
            # Get database path from repository (resolved path)
            db_path = repo.get_resolved_db_path()
            
            return {
                "wal": journal_mode == "wal",
                "foreign_keys": bool(foreign_keys),
                "page_size": page_size,
                "path": db_path
            }
    except Exception as e:
        return {
            "wal": False,
            "foreign_keys": False,
            "page_size": 0,
            "path": None,
            "error": str(e)
        }

async def _check_features() -> Dict[str, bool]:
    """Check feature availability."""
    # Check if LLM is enabled via environment variable
    llm_enabled = os.getenv("LLM_ENABLED", "false").lower() == "true"
    
    # Check if LLM model file exists (if enabled)
    if llm_enabled:
        model_path = os.getenv("LLM_MODEL_PATH", "llm/models/model.gguf")
        llm_enabled = os.path.exists(model_path)
    
    return {
        "llm": llm_enabled
    }
