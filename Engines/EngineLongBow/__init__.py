"""
EngineLongBow - Path-based ingest system for Lorien.

This engine replaces the traditional sibling-based import with a path-based approach
where each row represents a flow: D0→D1→…→D6.

Components:
- ingest: Read CSV/XLSX files and extract paths
- store: Idempotent storage of paths as nodes/edges
- present: Export current graph back to frozen 8-column format
- consts: Frozen header constants
"""

from .ingest import ingest_file, read_file, extract_paths, validate_header
from .store import apply_import, apply_import_with_metadata, ImportResult
from .present import export_paths, export_paths_to_csv, export_paths_to_xlsx
from .consts import FROZEN_HEADER, PATH_COLUMNS, NOTES_COLUMN

__all__ = [
    "ingest_file",
    "read_file", 
    "extract_paths",
    "validate_header",
    "apply_import",
    "apply_import_with_metadata",
    "ImportResult",
    "export_paths",
    "export_paths_to_csv",
    "export_paths_to_xlsx",
    "FROZEN_HEADER",
    "PATH_COLUMNS",
    "NOTES_COLUMN"
]
