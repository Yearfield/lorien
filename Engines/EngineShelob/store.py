"""
Pathogen data storage for EngineShelob.
Idempotent storage of pathogens and associations with transaction support.
"""

import sqlite3
from contextlib import contextmanager
from typing import Any, Optional

from .utils import normalize_pathogen_name


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
    """Result of pathogen import operation."""

    def __init__(self):
        self.pathogens_processed = 0
        self.pathogens_created = 0
        self.pathogens_updated = 0
        self.associations_processed = 0
        self.associations_created = 0
        self.errors = []
        self.warnings = []


def _get_or_create_association_type(conn: sqlite3.Connection, name: str) -> int:
    """Get or create an association type and return its ID."""
    cursor = conn.cursor()

    # Try to find existing association type
    cursor.execute("SELECT id FROM association_types WHERE name = ?", (name,))
    row = cursor.fetchone()

    if row:
        return row[0]

    # Create new association type
    cursor.execute("INSERT INTO association_types (name) VALUES (?)", (name,))
    return cursor.lastrowid


def _upsert_pathogen(conn: sqlite3.Connection, properties: dict[str, Any]) -> int:
    """
    Insert or update a pathogen and return its ID.

    Args:
        conn: Database connection
        properties: Pathogen properties dict

    Returns:
        Pathogen ID
    """
    cursor = conn.cursor()

    # Normalize pathogen name for lookup
    pathogen_name = normalize_pathogen_name(properties.get("pathogen_name"))
    if not pathogen_name:
        raise ValueError("Pathogen name is required")

    # Try to find existing pathogen by name
    cursor.execute("SELECT id FROM pathogens WHERE pathogen_name = ?", (pathogen_name,))
    row = cursor.fetchone()

    if row:
        # Update existing pathogen
        pathogen_id = row[0]
        cursor.execute(
            """
            UPDATE pathogens SET
                classification = ?,
                nt = ?,
                pathogen_id = ?,
                vaccine = ?,
                toxin = ?,
                transmission = ?,
                ab_resistance = ?,
                host = ?,
                commensal = ?,
                disease = ?,
                incubation = ?,
                diagnosis = ?,
                treatment = ?,
                prevention = ?,
                notes = ?
            WHERE id = ?
        """,
            (
                properties.get("classification"),
                properties.get("nt"),
                properties.get("pathogen_id"),
                properties.get("vaccine"),
                properties.get("toxin"),
                properties.get("transmission"),
                properties.get("ab_resistance"),
                properties.get("host"),
                properties.get("commensal"),
                properties.get("disease"),
                properties.get("incubation"),
                properties.get("diagnosis"),
                properties.get("treatment"),
                properties.get("prevention"),
                properties.get("notes"),
                pathogen_id,
            ),
        )
        return pathogen_id
    else:
        # Insert new pathogen
        cursor.execute(
            """
            INSERT INTO pathogens (
                classification, nt, pathogen_id, pathogen_name, vaccine, toxin,
                transmission, ab_resistance, host, commensal, disease, incubation,
                diagnosis, treatment, prevention, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                properties.get("classification"),
                properties.get("nt"),
                properties.get("pathogen_id"),
                pathogen_name,
                properties.get("vaccine"),
                properties.get("toxin"),
                properties.get("transmission"),
                properties.get("ab_resistance"),
                properties.get("host"),
                properties.get("commensal"),
                properties.get("disease"),
                properties.get("incubation"),
                properties.get("diagnosis"),
                properties.get("treatment"),
                properties.get("prevention"),
                properties.get("notes"),
            ),
        )
        return cursor.lastrowid


def _upsert_pathogen_associations(
    conn: sqlite3.Connection, pathogen_id: int, associations: dict[str, int]
) -> int:
    """
    Insert or update pathogen associations.

    Args:
        conn: Database connection
        pathogen_id: Pathogen ID
        associations: Dict of association_name -> value (0 or 1)

    Returns:
        Number of associations processed
    """
    cursor = conn.cursor()

    # Delete existing associations for this pathogen (idempotent behavior)
    cursor.execute("DELETE FROM pathogen_associations WHERE pathogen_id = ?", (pathogen_id,))

    # Insert new associations (only store 1s to keep database light)
    associations_created = 0
    for assoc_name, value in associations.items():
        if value == 1:  # Only store positive associations
            assoc_type_id = _get_or_create_association_type(conn, assoc_name)
            cursor.execute(
                """
                INSERT INTO pathogen_associations (pathogen_id, association_type_id, value)
                VALUES (?, ?, ?)
            """,
                (pathogen_id, assoc_type_id, 1),
            )
            associations_created += 1

    return associations_created


def apply_import(
    db_path: str, ingested_data: dict[str, Any], strategy: str = "upsert"
) -> ImportResult:
    """
    Apply imported pathogen data to database.

    Args:
        db_path: Path to SQLite database
        ingested_data: Data from ingest_file()
        strategy: Import strategy ("upsert" only for now)

    Returns:
        ImportResult with operation summary
    """
    result = ImportResult()

    if not ingested_data.get("success"):
        result.errors.extend(ingested_data.get("errors", []))
        return result

    data = ingested_data.get("data", {})
    pathogens = data.get("pathogens", [])

    with get_db_connection(db_path) as conn:
        try:
            for pathogen_data in pathogens:
                try:
                    properties = pathogen_data.get("properties", {})
                    associations = pathogen_data.get("associations", {})

                    # Upsert pathogen
                    pathogen_id = _upsert_pathogen(conn, properties)
                    result.pathogens_processed += 1

                    # Determine if this was a create or update
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT created_at, updated_at FROM pathogens WHERE id = ?", (pathogen_id,)
                    )
                    row = cursor.fetchone()
                    if row and row[0] == row[1]:  # created_at == updated_at means new
                        result.pathogens_created += 1
                    else:
                        result.pathogens_updated += 1

                    # Upsert associations
                    assoc_count = _upsert_pathogen_associations(conn, pathogen_id, associations)
                    result.associations_processed += len(associations)
                    result.associations_created += assoc_count

                except Exception as e:
                    error_msg = f"Error processing pathogen '{properties.get('pathogen_name', 'unknown')}': {str(e)}"
                    result.errors.append(error_msg)

            conn.commit()

        except Exception as e:
            conn.rollback()
            result.errors.append(f"Database transaction failed: {str(e)}")

    return result


def apply_import_with_metadata(
    db_path: str,
    ingested_data: dict[str, Any],
    strategy: str = "upsert",
    metadata: Optional[dict[str, Any]] = None,
) -> ImportResult:
    """
    Apply imported pathogen data with additional metadata.

    Args:
        db_path: Path to SQLite database
        ingested_data: Data from ingest_file()
        strategy: Import strategy
        metadata: Additional metadata (currently unused)

    Returns:
        ImportResult with operation summary
    """
    # For now, just call the basic apply_import
    # Future enhancement: store import metadata in separate table
    return apply_import(db_path, ingested_data, strategy)
