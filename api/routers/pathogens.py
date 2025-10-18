"""
Pathogen API router for EngineShelob.
Provides CRUD operations and import functionality for pathogen data.
"""

import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from api.settings import get_db_path
from Engines.EngineShelob import apply_import, ingest_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/pathogens", tags=["pathogens"])


# Pydantic models for request/response
class PathogenProperties(BaseModel):
    classification: Optional[str] = None
    nt: Optional[str] = None
    pathogen_id: Optional[str] = None
    pathogen_name: str
    vaccine: Optional[str] = None
    toxin: Optional[str] = None
    transmission: Optional[str] = None
    ab_resistance: Optional[str] = None
    host: Optional[str] = None
    commensal: Optional[str] = None
    disease: Optional[str] = None
    incubation: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    prevention: Optional[str] = None
    notes: Optional[str] = None


class PathogenResponse(BaseModel):
    id: int
    classification: Optional[str] = None
    nt: Optional[str] = None
    pathogen_id: Optional[str] = None
    pathogen_name: str
    vaccine: Optional[str] = None
    toxin: Optional[str] = None
    transmission: Optional[str] = None
    ab_resistance: Optional[str] = None
    host: Optional[str] = None
    commensal: Optional[str] = None
    disease: Optional[str] = None
    incubation: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment: Optional[str] = None
    prevention: Optional[str] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str


class AssociationResponse(BaseModel):
    association_type: str
    value: int


class PathogenAssociationResponse(BaseModel):
    pathogen_id: int
    association_type_id: int
    value: int
    association_type_name: str


class PathogenWithAssociationsResponse(PathogenResponse):
    associations: list[PathogenAssociationResponse] = []


class ImportResultResponse(BaseModel):
    success: bool
    pathogens_processed: int
    pathogens_created: int
    pathogens_updated: int
    associations_processed: int
    associations_created: int
    errors: list[str] = []
    warnings: list[str] = []


# Dependency to get database path
def get_database_path() -> str:
    """Get the database path."""
    return get_db_path()


@router.get("/", response_model=list[PathogenResponse])
async def list_pathogens(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of pathogens to return"),
    offset: int = Query(0, ge=0, description="Number of pathogens to skip"),
    search: Optional[str] = Query(None, description="Search term for pathogen name"),
    association_filter: Optional[str] = Query(None, description="Filter by association type"),
    show_only_with_associations: bool = Query(
        False, description="Show only pathogens with associations"
    ),
    db_path: str = Depends(get_database_path),
):
    """List pathogens with optional search and pagination."""
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Build query with optional search and filters
        query = "SELECT DISTINCT p.* FROM pathogens p"
        params = []
        conditions = []

        # Add association filter if specified
        if association_filter or show_only_with_associations:
            query += " LEFT JOIN pathogen_associations pa ON p.id = pa.pathogen_id"
            if association_filter:
                query += " LEFT JOIN association_types at ON pa.association_type_id = at.id"
                conditions.append("at.name = ?")
                params.append(association_filter)

        if search:
            conditions.append("p.pathogen_name LIKE ?")
            params.append(f"%{search}%")

        if show_only_with_associations:
            conditions.append("pa.pathogen_id IS NOT NULL")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY p.pathogen_name LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [PathogenResponse(**dict(row)) for row in rows]


@router.get("/{pathogen_id}", response_model=PathogenWithAssociationsResponse)
async def get_pathogen(pathogen_id: int, db_path: str = Depends(get_database_path)):
    """Get a single pathogen with its associations."""
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get pathogen
        cursor.execute("SELECT * FROM pathogens WHERE id = ?", (pathogen_id,))
        pathogen_row = cursor.fetchone()

        if not pathogen_row:
            raise HTTPException(status_code=404, detail="Pathogen not found")

        # Get associations
        cursor.execute(
            """
            SELECT pa.pathogen_id, pa.association_type_id, pa.value, at.name as association_type_name
            FROM pathogen_associations pa
            JOIN association_types at ON pa.association_type_id = at.id
            WHERE pa.pathogen_id = ?
        """,
            (pathogen_id,),
        )
        association_rows = cursor.fetchall()

        associations = [
            PathogenAssociationResponse(
                pathogen_id=row["pathogen_id"],
                association_type_id=row["association_type_id"],
                value=row["value"],
                association_type_name=row["association_type_name"],
            )
            for row in association_rows
        ]

        pathogen_data = dict(pathogen_row)
        pathogen_data["associations"] = associations

        return PathogenWithAssociationsResponse(**pathogen_data)


@router.get("/{pathogen_id}/associations", response_model=list[AssociationResponse])
async def get_pathogen_associations(pathogen_id: int, db_path: str = Depends(get_database_path)):
    """Get associations for a specific pathogen."""
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Verify pathogen exists
        cursor.execute("SELECT id FROM pathogens WHERE id = ?", (pathogen_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Pathogen not found")

        # Get associations
        cursor.execute(
            """
            SELECT at.name as association_type, pa.value
            FROM pathogen_associations pa
            JOIN association_types at ON pa.association_type_id = at.id
            WHERE pa.pathogen_id = ?
        """,
            (pathogen_id,),
        )
        rows = cursor.fetchall()

        return [
            AssociationResponse(association_type=row["association_type"], value=row["value"])
            for row in rows
        ]


@router.get("/association-types/", response_model=list[str])
async def list_association_types(db_path: str = Depends(get_database_path)):
    """List all association types."""
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM association_types ORDER BY name")
        rows = cursor.fetchall()

        return [row[0] for row in rows]


@router.post("/import", response_model=ImportResultResponse)
async def import_pathogens(
    file: UploadFile = File(..., description="CSV or XLSX file containing pathogen data"),
    strategy: str = Query("upsert", description="Import strategy (upsert only)"),
    db_path: str = Depends(get_database_path),
):
    """Import pathogen data from a spreadsheet file."""

    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    file_ext = os.path.splitext(file.filename.lower())[1]
    if file_ext not in [".csv", ".xlsx", ".xls"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Supported types: .csv, .xlsx, .xls",
        )

    # Validate file size (50MB limit)
    file_content = await file.read()
    if len(file_content) > 50 * 1024 * 1024:  # 50MB
        raise HTTPException(status_code=413, detail="File too large. Maximum size: 50MB")

    try:
        # Ingest file
        logger.info(f"Importing pathogen file: {file.filename}")
        ingested_data = ingest_file(file_content, file.filename)

        if not ingested_data["success"]:
            return ImportResultResponse(
                success=False,
                pathogens_processed=0,
                pathogens_created=0,
                pathogens_updated=0,
                associations_processed=0,
                associations_created=0,
                errors=ingested_data.get("errors", []),
            )

        # Apply import to database
        result = apply_import(db_path, ingested_data, strategy)

        logger.info(
            f"Pathogen import completed: {result.pathogens_processed} pathogens processed, "
            f"{result.pathogens_created} created, {result.pathogens_updated} updated"
        )

        return ImportResultResponse(
            success=len(result.errors) == 0,
            pathogens_processed=result.pathogens_processed,
            pathogens_created=result.pathogens_created,
            pathogens_updated=result.pathogens_updated,
            associations_processed=result.associations_processed,
            associations_created=result.associations_created,
            errors=result.errors,
            warnings=result.warnings,
        )

    except Exception as e:
        logger.error(f"Pathogen import failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/stats/summary")
async def get_pathogen_stats(db_path: str = Depends(get_database_path)):
    """Get summary statistics about pathogen data."""
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get pathogen count
        cursor.execute("SELECT COUNT(*) FROM pathogens")
        pathogen_count = cursor.fetchone()[0]

        # Get association type count
        cursor.execute("SELECT COUNT(*) FROM association_types")
        association_type_count = cursor.fetchone()[0]

        # Get total associations count
        cursor.execute("SELECT COUNT(*) FROM pathogen_associations")
        total_associations = cursor.fetchone()[0]

        # Get pathogens with associations count
        cursor.execute(
            """
            SELECT COUNT(DISTINCT pathogen_id)
            FROM pathogen_associations
        """
        )
        pathogens_with_associations = cursor.fetchone()[0]

        # Calculate average associations per pathogen
        average_associations = total_associations / pathogen_count if pathogen_count > 0 else 0.0

        return {
            "total_pathogens": pathogen_count,
            "total_association_types": association_type_count,
            "total_associations": total_associations,
            "pathogens_with_associations": pathogens_with_associations,
            "pathogens_without_associations": pathogen_count - pathogens_with_associations,
            "average_associations_per_pathogen": round(average_associations, 2),
        }


@router.post("/", response_model=PathogenResponse)
async def create_pathogen(pathogen_data: PathogenProperties, db_path: str = Depends(get_db_path)):
    """Create a new pathogen."""
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO pathogens (
                classification, nt, pathogen_id, pathogen_name, vaccine, toxin,
                transmission, ab_resistance, host, commensal, disease, incubation,
                diagnosis, treatment, prevention, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                pathogen_data.classification,
                pathogen_data.nt,
                pathogen_data.pathogen_id,
                pathogen_data.pathogen_name,
                pathogen_data.vaccine,
                pathogen_data.toxin,
                pathogen_data.transmission,
                pathogen_data.ab_resistance,
                pathogen_data.host,
                pathogen_data.commensal,
                pathogen_data.disease,
                pathogen_data.incubation,
                pathogen_data.diagnosis,
                pathogen_data.treatment,
                pathogen_data.prevention,
                pathogen_data.notes,
            ),
        )

        pathogen_id = cursor.lastrowid

        # Fetch the created pathogen
        cursor.execute("SELECT * FROM pathogens WHERE id = ?", (pathogen_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Pathogen not found after creation")

        return PathogenResponse(**dict(row))


@router.put("/{pathogen_id}", response_model=PathogenResponse)
async def update_pathogen(
    pathogen_id: int, pathogen_data: PathogenProperties, db_path: str = Depends(get_db_path)
):
    """Update an existing pathogen."""
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Check if pathogen exists
        cursor.execute("SELECT id FROM pathogens WHERE id = ?", (pathogen_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Pathogen not found")

        cursor.execute(
            """
            UPDATE pathogens SET
                classification = ?, nt = ?, pathogen_id = ?, pathogen_name = ?,
                vaccine = ?, toxin = ?, transmission = ?, ab_resistance = ?,
                host = ?, commensal = ?, disease = ?, incubation = ?,
                diagnosis = ?, treatment = ?, prevention = ?, notes = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
            (
                pathogen_data.classification,
                pathogen_data.nt,
                pathogen_data.pathogen_id,
                pathogen_data.pathogen_name,
                pathogen_data.vaccine,
                pathogen_data.toxin,
                pathogen_data.transmission,
                pathogen_data.ab_resistance,
                pathogen_data.host,
                pathogen_data.commensal,
                pathogen_data.disease,
                pathogen_data.incubation,
                pathogen_data.diagnosis,
                pathogen_data.treatment,
                pathogen_data.prevention,
                pathogen_data.notes,
                pathogen_id,
            ),
        )

        # Fetch the updated pathogen
        cursor.execute("SELECT * FROM pathogens WHERE id = ?", (pathogen_id,))
        row = cursor.fetchone()

        return PathogenResponse(**dict(row))
