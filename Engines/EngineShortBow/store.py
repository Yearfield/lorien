"""
Data storage for EngineShortBow symptom matrix.
"""

import logging
import sqlite3
from dataclasses import dataclass
from typing import Optional

from .utils import normalize_symptom_name

logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    """Result of importing symptom matrix data."""

    success: bool
    symptoms_processed: int = 0
    symptoms_created: int = 0
    symptoms_updated: int = 0
    links_processed: int = 0
    links_created: int = 0
    links_updated: int = 0
    errors: list[str] = None
    warnings: list[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


def apply_import(
    conn: sqlite3.Connection, symptoms: list[str], symptom_links: dict[tuple[str, str], float]
) -> ImportResult:
    """
    Apply symptom matrix import to database.

    Args:
        conn: Database connection
        symptoms: List of symptom names
        symptom_links: Dict mapping (from_symptom, to_symptom) -> probability

    Returns:
        ImportResult with import statistics
    """
    result = ImportResult(success=True)

    try:
        # Import symptoms
        symptom_id_map = {}

        for symptom in symptoms:
            normalized = normalize_symptom_name(symptom)

            # Check if symptom exists
            cursor = conn.execute(
                "SELECT id FROM shortbow_symptoms WHERE symptom_name = ?", (normalized,)
            )
            existing = cursor.fetchone()

            if existing:
                symptom_id_map[normalized] = existing[0]
                result.symptoms_updated += 1
            else:
                # Insert new symptom
                cursor = conn.execute(
                    "INSERT INTO shortbow_symptoms (symptom_name) VALUES (?)", (normalized,)
                )
                symptom_id_map[normalized] = cursor.lastrowid
                result.symptoms_created += 1

            result.symptoms_processed += 1

        # Import symptom links
        for (from_symptom, to_symptom), probability in symptom_links.items():
            from_id = symptom_id_map.get(from_symptom)
            to_id = symptom_id_map.get(to_symptom)

            if not from_id or not to_id:
                result.warnings.append(f"Missing symptom IDs for {from_symptom} -> {to_symptom}")
                continue

            # Check if link exists
            cursor = conn.execute(
                "SELECT id FROM shortbow_symptom_links WHERE symptom_from_id = ? AND symptom_to_id = ?",
                (from_id, to_id),
            )
            existing = cursor.fetchone()

            if existing:
                # Update existing link
                conn.execute(
                    "UPDATE shortbow_symptom_links SET probability = ?, updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id = ?",
                    (probability, existing[0]),
                )
                result.links_updated += 1
            else:
                # Insert new link
                conn.execute(
                    "INSERT INTO shortbow_symptom_links (symptom_from_id, symptom_to_id, probability) VALUES (?, ?, ?)",
                    (from_id, to_id, probability),
                )
                result.links_created += 1

            result.links_processed += 1

        conn.commit()
        logger.info(
            f"Import completed: {result.symptoms_created} symptoms created, {result.links_created} links created"
        )

    except Exception as e:
        result.success = False
        result.errors.append(f"Database error: {e}")
        logger.error(f"Import failed: {e}")
        conn.rollback()

    return result


def apply_import_with_metadata(
    conn: sqlite3.Connection,
    symptoms: list[str],
    symptom_links: dict[tuple[str, str], float],
    metadata: Optional[dict] = None,
) -> ImportResult:
    """
    Apply import with optional metadata (currently same as apply_import).

    Args:
        conn: Database connection
        symptoms: List of symptom names
        symptom_links: Dict mapping (from_symptom, to_symptom) -> probability
        metadata: Optional metadata (not used currently)

    Returns:
        ImportResult with import statistics
    """
    return apply_import(conn, symptoms, symptom_links)
