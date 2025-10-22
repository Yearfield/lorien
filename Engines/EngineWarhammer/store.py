"""
Data storage for EngineWarhammer.
Idempotent storage of diseases, symptoms, and conditional probabilities with transaction support.
"""

import json
import logging
import sqlite3
from contextlib import contextmanager
from typing import Any, Optional

from .utils import normalize_disease_name, normalize_symptom_name

logger = logging.getLogger(__name__)


def _get_conn(db_path: str):
    """Get database connection using provided path."""
    return sqlite3.connect(db_path)


@contextmanager
def get_db_connection(db_path: str):
    """Context manager for database connections."""
    conn = _get_conn(db_path)
    try:
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
    finally:
        conn.close()


class ImportResult:
    """Result of Warhammer data import operation."""

    def __init__(self):
        self.diseases_processed = 0
        self.diseases_created = 0
        self.diseases_updated = 0
        self.symptoms_processed = 0
        self.symptoms_created = 0
        self.symptoms_updated = 0
        self.conditionals_processed = 0
        self.conditionals_created = 0
        self.conditionals_updated = 0
        self.errors = []
        self.warnings = []


def _get_or_create_disease(
    conn: sqlite3.Connection, disease_name: str, estimated_lifetime_risk: float
) -> int:
    """Get or create a disease and return its ID."""
    cursor = conn.cursor()

    # Try to find existing disease
    cursor.execute("SELECT id FROM diseases WHERE disease_name = ?", (disease_name,))
    row = cursor.fetchone()

    if row:
        # Update existing disease
        disease_id = row[0]
        cursor.execute(
            "UPDATE diseases SET estimated_lifetime_risk = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (estimated_lifetime_risk, disease_id),
        )
        return disease_id

    # Create new disease
    cursor.execute(
        "INSERT INTO diseases (disease_name, estimated_lifetime_risk) VALUES (?, ?)",
        (disease_name, estimated_lifetime_risk),
    )
    return cursor.lastrowid


def _get_or_create_symptom(conn: sqlite3.Connection, symptom_name: str, probability: float) -> int:
    """Get or create a symptom and return its ID."""
    cursor = conn.cursor()

    # Try to find existing symptom
    cursor.execute("SELECT id FROM symptoms WHERE symptom_name = ?", (symptom_name,))
    row = cursor.fetchone()

    if row:
        # Update existing symptom
        symptom_id = row[0]
        cursor.execute(
            "UPDATE symptoms SET probability = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (probability, symptom_id),
        )
        return symptom_id

    # Create new symptom
    cursor.execute(
        "INSERT INTO symptoms (symptom_name, probability) VALUES (?, ?)",
        (symptom_name, probability),
    )
    return cursor.lastrowid


def _upsert_conditional(
    conn: sqlite3.Connection, symptom_id: int, disease_id: int, conditional_probability: float
) -> int:
    """Insert or update a conditional probability and return its ID."""
    cursor = conn.cursor()

    # Try to find existing conditional
    cursor.execute(
        "SELECT id FROM symptom_disease_conditionals WHERE symptom_id = ? AND disease_id = ?",
        (symptom_id, disease_id),
    )
    row = cursor.fetchone()

    if row:
        # Update existing conditional
        conditional_id = row[0]
        cursor.execute(
            "UPDATE symptom_disease_conditionals SET conditional_probability = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (conditional_probability, conditional_id),
        )
        return conditional_id

    # Create new conditional
    cursor.execute(
        "INSERT INTO symptom_disease_conditionals (symptom_id, disease_id, conditional_probability) VALUES (?, ?, ?)",
        (symptom_id, disease_id, conditional_probability),
    )
    return cursor.lastrowid


def apply_disease_import(db_path: str, disease_data: list[dict[str, Any]]) -> ImportResult:
    """Apply disease data import to database."""
    result = ImportResult()

    with get_db_connection(db_path) as conn:
        try:
            for disease in disease_data:
                try:
                    disease_name = normalize_disease_name(disease.get("disease_name"))
                    if not disease_name:
                        result.errors.append(f"Invalid disease name: {disease.get('disease_name')}")
                        continue

                    estimated_lifetime_risk = disease.get("estimated_lifetime_risk")
                    if estimated_lifetime_risk is None:
                        result.errors.append(
                            f"Missing estimated lifetime risk for disease: {disease_name}"
                        )
                        continue

                    _get_or_create_disease(conn, disease_name, estimated_lifetime_risk)
                    result.diseases_processed += 1
                    result.diseases_created += 1  # Simplified - could track updates separately

                except Exception as e:
                    result.errors.append(
                        f"Error processing disease {disease.get('disease_name', 'unknown')}: {str(e)}"
                    )

            conn.commit()

        except Exception as e:
            conn.rollback()
            result.errors.append(f"Database error during disease import: {str(e)}")

    return result


def apply_symptom_import(db_path: str, symptom_data: list[dict[str, Any]]) -> ImportResult:
    """Apply symptom data import to database."""
    result = ImportResult()

    with get_db_connection(db_path) as conn:
        try:
            for symptom in symptom_data:
                try:
                    symptom_name = normalize_symptom_name(symptom.get("symptom_name"))
                    if not symptom_name:
                        result.errors.append(f"Invalid symptom name: {symptom.get('symptom_name')}")
                        continue

                    probability = symptom.get("probability")
                    if probability is None:
                        result.errors.append(f"Missing probability for symptom: {symptom_name}")
                        continue

                    _get_or_create_symptom(conn, symptom_name, probability)
                    result.symptoms_processed += 1
                    result.symptoms_created += 1  # Simplified - could track updates separately

                except Exception as e:
                    result.errors.append(
                        f"Error processing symptom {symptom.get('symptom_name', 'unknown')}: {str(e)}"
                    )

            conn.commit()

        except Exception as e:
            conn.rollback()
            result.errors.append(f"Database error during symptom import: {str(e)}")

    return result


def apply_conditional_import(db_path: str, conditional_data: list[dict[str, Any]]) -> ImportResult:
    """Apply conditional probability data import to database."""
    result = ImportResult()

    with get_db_connection(db_path) as conn:
        try:
            for conditional in conditional_data:
                try:
                    symptom_name = normalize_symptom_name(conditional.get("symptom_name"))
                    disease_name = normalize_disease_name(conditional.get("disease_name"))

                    if not symptom_name:
                        result.errors.append(
                            f"Invalid symptom name: {conditional.get('symptom_name')}"
                        )
                        continue

                    if not disease_name:
                        result.errors.append(
                            f"Invalid disease name: {conditional.get('disease_name')}"
                        )
                        continue

                    conditional_probability = conditional.get("conditional_probability")
                    if conditional_probability is None:
                        result.errors.append(
                            f"Missing conditional probability for symptom '{symptom_name}' and disease '{disease_name}'"
                        )
                        continue

                    # Get or create symptom and disease IDs
                    symptom_id = _get_or_create_symptom(
                        conn, symptom_name, 0.0
                    )  # Placeholder probability
                    disease_id = _get_or_create_disease(conn, disease_name, 0.0)  # Placeholder risk

                    _upsert_conditional(conn, symptom_id, disease_id, conditional_probability)
                    result.conditionals_processed += 1
                    result.conditionals_created += 1  # Simplified - could track updates separately

                except Exception as e:
                    result.errors.append(
                        f"Error processing conditional {conditional.get('symptom_name', 'unknown')} -> {conditional.get('disease_name', 'unknown')}: {str(e)}"
                    )

            conn.commit()

        except Exception as e:
            conn.rollback()
            result.errors.append(f"Database error during conditional import: {str(e)}")

    return result


def apply_import(db_path: str, ingested_data: dict[str, Any], import_type: str) -> ImportResult:
    """
    Apply imported data to database based on type.

    Args:
        db_path: Path to database file
        ingested_data: Data extracted from file
        import_type: Type of import ('diseases', 'symptoms', or 'conditionals')

    Returns:
        ImportResult with operation statistics
    """
    if not ingested_data.get("success", False):
        result = ImportResult()
        result.errors = ingested_data.get("errors", ["Unknown import error"])
        return result

    data = ingested_data.get("data", [])

    if import_type == "diseases":
        return apply_disease_import(db_path, data)
    elif import_type == "symptoms":
        return apply_symptom_import(db_path, data)
    elif import_type == "conditionals":
        return apply_conditional_import(db_path, data)
    else:
        result = ImportResult()
        result.errors.append(f"Unknown import type: {import_type}")
        return result


def apply_import_with_metadata(
    db_path: str, ingested_data: dict[str, Any], import_type: str, metadata: dict[str, Any]
) -> ImportResult:
    """
    Apply imported data with additional metadata.

    Args:
        db_path: Path to database file
        ingested_data: Data extracted from file
        import_type: Type of import
        metadata: Additional metadata about the import

    Returns:
        ImportResult with operation statistics
    """
    result = apply_import(db_path, ingested_data, import_type)

    # Add metadata to warnings if provided
    if metadata:
        result.warnings.append(f"Import metadata: {json.dumps(metadata)}")

    return result


def save_calculation(db_path: str, calculation_result, input_symptoms: list[str]) -> int:
    """
    Save a calculation result to the database.

    Args:
        db_path: Path to database file
        calculation_result: WarhammerCalculationResult object
        input_symptoms: List of input symptoms

    Returns:
        ID of saved calculation
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # Prepare results data
        results_data = [
            {"disease": result.disease_name, "probability": result.probability}
            for result in calculation_result.results
        ]

        cursor.execute(
            """
            INSERT INTO warhammer_calculations (input_symptoms, results, saved)
            VALUES (?, ?, ?)
            """,
            (json.dumps(input_symptoms), json.dumps(results_data), True),
        )

        conn.commit()
        return cursor.lastrowid


def get_calculation(db_path: str, calculation_id: int) -> Optional[dict[str, Any]]:
    """
    Retrieve a saved calculation from the database.

    Args:
        db_path: Path to database file
        calculation_id: ID of calculation to retrieve

    Returns:
        Calculation data or None if not found
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM warhammer_calculations WHERE id = ?", (calculation_id,))
        row = cursor.fetchone()

        if not row:
            return None

        return {
            "id": row[0],
            "calculation_date": row[1],
            "input_symptoms": json.loads(row[2]),
            "results": json.loads(row[3]),
            "saved": bool(row[4]),
        }


def list_calculations(db_path: str, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    """
    List saved calculations from the database.

    Args:
        db_path: Path to database file
        limit: Maximum number of calculations to return
        offset: Number of calculations to skip

    Returns:
        List of calculation data
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, calculation_date, input_symptoms, results, saved
            FROM warhammer_calculations
            WHERE saved = 1
            ORDER BY calculation_date DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        )

        calculations = []
        for row in cursor.fetchall():
            calculations.append(
                {
                    "id": row[0],
                    "calculation_date": row[1],
                    "input_symptoms": json.loads(row[2]),
                    "results": json.loads(row[3]),
                    "saved": bool(row[4]),
                }
            )

        return calculations
