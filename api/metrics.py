"""
Telemetry and analytics for the Lorien application.
Non-PHI counters for system usage and performance monitoring.
"""

import os
from typing import Dict, Any

# Feature flag for telemetry
ENABLED = os.getenv("ANALYTICS_ENABLED", "false").lower() == "true"

# In-memory counters (in production, use Redis or similar)
COUNTERS: Dict[str, int] = {}

def incr(name: str) -> None:
    """Increment a counter if telemetry is enabled."""
    if ENABLED:
        COUNTERS[name] = COUNTERS.get(name, 0) + 1

def snapshot() -> Dict[str, Any]:
    """Get a snapshot of current metrics if telemetry is enabled."""
    if not ENABLED:
        return {}
    
    return {
        "counters": dict(COUNTERS),
        "enabled": True,
        "timestamp": "2025-01-01T00:00:00Z"  # In production, use actual timestamp
    }

def reset() -> None:
    """Reset all counters (for testing)."""
    COUNTERS.clear()

# Predefined metric names for consistency
class Metrics:
    # Page hits
    PAGE_WORKSPACE = "page_workspace"
    PAGE_CONFLICTS = "page_conflicts"
    PAGE_OUTCOMES = "page_outcomes"
    PAGE_EDITOR = "page_editor"
    
    # Import/Export operations
    IMPORT_EXCEL_SUCCESS = "import_excel_success"
    IMPORT_EXCEL_ERROR = "import_excel_error"
    EXPORT_CSV_SUCCESS = "export_csv_success"
    EXPORT_CSV_ERROR = "export_csv_error"
    EXPORT_XLSX_SUCCESS = "export_xlsx_success"
    EXPORT_XLSX_ERROR = "export_xlsx_error"
    
    # Cascade operations
    FLAGS_CASCADE_ASSIGN = "flags_cascade_assign"
    FLAGS_CASCADE_REMOVE = "flags_cascade_remove"
    
    # LLM operations
    LLM_FILL_REQUESTED = "llm_fill_requested"
    LLM_FILL_SUCCESS = "llm_fill_success"
    LLM_FILL_ERROR = "llm_fill_error"
    
    # Database operations
    BACKUP_CREATED = "backup_created"
    BACKUP_ERROR = "backup_error"
    RESTORE_COMPLETED = "restore_completed"
    RESTORE_ERROR = "restore_error"
