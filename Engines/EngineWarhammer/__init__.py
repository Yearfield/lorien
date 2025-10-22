"""
EngineWarhammer - Bayesian disease probability calculator for Lorien.

This engine calculates disease probabilities based on observed symptoms using
Bayesian inference. It imports disease and symptom data from CSV files and
provides probability calculations for diagnostic support.

Components:
- ingest: Read CSV/XLSX files and extract disease/symptom data
- store: Idempotent storage of diseases, symptoms, and conditional probabilities
- calculator: Core Bayesian calculation logic
- consts: Column mapping and data structure definitions
- utils: Normalization helpers for disease/symptom names
"""

from .calculator import WarhammerCalculationResult, calculate_disease_probabilities
from .consts import CONDITIONAL_COLUMNS, DISEASE_COLUMNS, SYMPTOM_COLUMNS
from .ingest import (
    extract_conditional_data,
    extract_disease_data,
    extract_symptom_data,
    ingest_file,
)
from .store import ImportResult, apply_import, apply_import_with_metadata
from .utils import normalize_disease_name, normalize_symptom_name

__all__ = [
    "ingest_file",
    "extract_disease_data",
    "extract_symptom_data",
    "extract_conditional_data",
    "apply_import",
    "apply_import_with_metadata",
    "ImportResult",
    "calculate_disease_probabilities",
    "WarhammerCalculationResult",
    "DISEASE_COLUMNS",
    "SYMPTOM_COLUMNS",
    "CONDITIONAL_COLUMNS",
    "normalize_disease_name",
    "normalize_symptom_name",
]
