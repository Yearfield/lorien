"""
EngineShortBow - Interactive symptom navigator based on conditional probabilities.

This engine provides symptom navigation using a probability matrix where rows and columns
are symptom names, and cell values are probabilities (0-1) of linkage/co-occurrence between symptoms.
It helps users navigate through related symptoms in a differential diagnosis workflow.

Components:
- ingest: Read Excel matrix files and extract symptom data
- store: Idempotent storage of symptom matrix data
- calculator: Core navigation logic for finding linked symptoms
- consts: Column mapping and data structure definitions
- utils: Normalization helpers for symptom names
"""

from .calculator import ShortBowCalculationResult, get_top_linked_symptoms
from .consts import SYMPTOM_COLUMNS
from .ingest import extract_symptom_matrix, ingest_file
from .store import ImportResult, apply_import, apply_import_with_metadata
from .utils import normalize_symptom_name

__all__ = [
    "ingest_file",
    "extract_symptom_matrix",
    "apply_import",
    "apply_import_with_metadata",
    "ImportResult",
    "get_top_linked_symptoms",
    "ShortBowCalculationResult",
    "SYMPTOM_COLUMNS",
    "normalize_symptom_name",
]
