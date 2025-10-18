"""
EngineShelob - Pathogen data import system for Lorien.

This engine imports pathogen spreadsheets with properties and binary associations,
storing them in isolated database tables separate from the decision tree structure.

Components:
- ingest: Read CSV/XLSX files and extract pathogen data
- store: Idempotent storage of pathogens and associations
- consts: Column mapping and detection logic
- utils: Normalization helpers
"""

from .consts import ASSOCIATION_DETECTION_PATTERNS, PROPERTY_COLUMNS
from .ingest import extract_pathogen_data, ingest_file, read_file
from .store import ImportResult, apply_import, apply_import_with_metadata
from .utils import normalize_pathogen_name, normalize_value

__all__ = [
    "ingest_file",
    "read_file",
    "extract_pathogen_data",
    "apply_import",
    "apply_import_with_metadata",
    "ImportResult",
    "PROPERTY_COLUMNS",
    "ASSOCIATION_DETECTION_PATTERNS",
    "normalize_pathogen_name",
    "normalize_value",
]
