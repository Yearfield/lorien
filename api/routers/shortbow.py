"""
ShortBow API router for EngineShortBow.
Provides CRUD operations, import functionality, and navigation endpoints for interactive symptom navigation.
"""

import logging
import sqlite3

import anyio
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from api.settings import get_db_path
from Engines.EngineShortBow import (
    apply_import,
    ingest_file,
)
from Engines.EngineShortBow.calculator import (
    get_top_linked_symptoms,
    get_top_symptoms_by_average_linkage,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/shortbow", tags=["shortbow"])


# Pydantic models for request/response
class SymptomResponse(BaseModel):
    id: int
    symptom_name: str
    created_at: str
    updated_at: str


class SymptomLinkResponse(BaseModel):
    from_symptom: str
    to_symptom: str
    probability: float


class NavigationRequest(BaseModel):
    current_symptom: str
    exclude: list[str] = []


class NavigationResponse(BaseModel):
    current_symptom: str
    top_linked: list[SymptomLinkResponse]
    excluded_symptoms: list[str]
    total_available: int


class CalculationRequest(BaseModel):
    initial_symptom: str
    selected_symptoms: list[str]


class CalculationResponse(BaseModel):
    id: int
    calculation_date: str
    initial_symptom: str
    selected_symptoms: list[str]
    saved: bool
    created_at: str


class ImportResultResponse(BaseModel):
    success: bool
    symptoms_processed: int = 0
    symptoms_created: int = 0
    symptoms_updated: int = 0
    links_processed: int = 0
    links_created: int = 0
    links_updated: int = 0
    errors: list[str] = []
    warnings: list[str] = []


class ShortBowStats(BaseModel):
    total_symptoms: int
    total_links: int
    total_calculations: int
    saved_calculations: int


# Dependency to get database connection
def get_db_connection() -> sqlite3.Connection:
    """Get database connection."""
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


@router.post("/import", response_model=ImportResultResponse)
async def import_symptom_matrix(
    file: UploadFile = File(...), conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Import symptom matrix from Excel file."""
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are supported")

    try:
        # Save uploaded file temporarily
        import tempfile

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file.flush()

            # Extract data from Excel
            symptoms, symptom_links = ingest_file(tmp_file.name)

            # Apply import to database using thread-offloaded approach
            def _apply_import():
                return apply_import(conn, symptoms, symptom_links)

            result = await anyio.to_thread.run_sync(_apply_import)

            return ImportResultResponse(
                success=result.success,
                symptoms_processed=result.symptoms_processed,
                symptoms_created=result.symptoms_created,
                symptoms_updated=result.symptoms_updated,
                links_processed=result.links_processed,
                links_created=result.links_created,
                links_updated=result.links_updated,
                errors=result.errors,
                warnings=result.warnings,
            )

    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise HTTPException(status_code=500, detail=f"Import failed: {e}")


@router.get("/symptoms", response_model=list[SymptomResponse])
async def get_symptoms(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Get list of available symptoms."""

    def _get_symptoms():
        cursor = conn.execute(
            "SELECT id, symptom_name, created_at, updated_at FROM shortbow_symptoms ORDER BY symptom_name LIMIT ? OFFSET ?",
            (limit, offset),
        )
        return cursor.fetchall()

    symptoms = await anyio.to_thread.run_sync(_get_symptoms)

    return [
        SymptomResponse(
            id=row["id"],
            symptom_name=row["symptom_name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
        for row in symptoms
    ]


@router.post("/navigate", response_model=NavigationResponse)
async def navigate_symptoms(
    request: NavigationRequest, conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Get top linked symptoms for navigation."""
    try:

        def _get_links_data():
            cursor = conn.execute(
                """
                SELECT
                    s1.symptom_name as from_symptom,
                    s2.symptom_name as to_symptom,
                    sl.probability
                FROM shortbow_symptom_links sl
                JOIN shortbow_symptoms s1 ON sl.symptom_from_id = s1.id
                JOIN shortbow_symptoms s2 ON sl.symptom_to_id = s2.id
            """
            )
            return cursor.fetchall()

        # Get all symptom links from database
        links_data = await anyio.to_thread.run_sync(_get_links_data)

        # Convert to dict format expected by calculator
        symptom_links = {}
        for row in links_data:
            key = (row["from_symptom"], row["to_symptom"])
            symptom_links[key] = row["probability"]

        # Get top linked symptoms
        result = get_top_linked_symptoms(
            current_symptom=request.current_symptom,
            symptom_links=symptom_links,
            exclude=request.exclude,
        )

        # Convert to response format
        top_linked = [
            SymptomLinkResponse(
                from_symptom=link.from_symptom,
                to_symptom=link.to_symptom,
                probability=link.probability,
            )
            for link in result.top_linked
        ]

        return NavigationResponse(
            current_symptom=result.current_symptom,
            top_linked=top_linked,
            excluded_symptoms=result.excluded_symptoms,
            total_available=result.total_available,
        )

    except Exception as e:
        logger.error(f"Navigation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Navigation failed: {e}")


@router.get("/top-symptoms", response_model=list[SymptomLinkResponse])
async def get_top_symptoms(
    limit: int = Query(6, ge=1, le=20), conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Get symptoms with highest average linkage to start navigation."""
    try:

        def _get_symptoms_and_links():
            # Create a new connection for this thread
            import sqlite3

            from api.dependencies import get_db_path

            db_path = get_db_path()
            thread_conn = sqlite3.connect(db_path)
            thread_conn.row_factory = sqlite3.Row

            try:
                # Get all symptoms
                cursor = thread_conn.execute("SELECT symptom_name FROM shortbow_symptoms")
                all_symptoms = [row["symptom_name"] for row in cursor.fetchall()]

                # Get all symptom links
                cursor = thread_conn.execute(
                    """
                    SELECT
                        s1.symptom_name as from_symptom,
                        s2.symptom_name as to_symptom,
                        sl.probability
                    FROM shortbow_symptom_links sl
                    JOIN shortbow_symptoms s1 ON sl.symptom_from_id = s1.id
                    JOIN shortbow_symptoms s2 ON sl.symptom_to_id = s2.id
                """
                )
                links_data = cursor.fetchall()

                return all_symptoms, links_data
            finally:
                thread_conn.close()

        # Get all symptoms and links
        all_symptoms, links_data = await anyio.to_thread.run_sync(_get_symptoms_and_links)

        # Convert to dict format
        symptom_links = {}
        for row in links_data:
            key = (row["from_symptom"], row["to_symptom"])
            symptom_links[key] = row["probability"]

        # Get top symptoms by average linkage
        top_symptoms = get_top_symptoms_by_average_linkage(
            symptom_links=symptom_links, all_symptoms=all_symptoms, max_results=limit
        )

        # Convert to response format (using dummy to_symptom for display)
        return [
            SymptomLinkResponse(from_symptom="", to_symptom=symptom, probability=avg_prob)
            for symptom, avg_prob in top_symptoms
        ]

    except Exception as e:
        logger.error(f"Top symptoms failed: {e}")
        raise HTTPException(status_code=500, detail=f"Top symptoms failed: {e}")


@router.get("/stats/summary", response_model=ShortBowStats)
async def get_stats(conn: sqlite3.Connection = Depends(get_db_connection)):
    """Get summary statistics."""
    try:

        def _get_stats():
            # Create a new connection for this thread
            import sqlite3

            from api.dependencies import get_db_path

            db_path = get_db_path()
            thread_conn = sqlite3.connect(db_path)
            thread_conn.row_factory = sqlite3.Row

            try:
                # Count symptoms
                cursor = thread_conn.execute("SELECT COUNT(*) as count FROM shortbow_symptoms")
                total_symptoms = cursor.fetchone()["count"]

                # Count links
                cursor = thread_conn.execute("SELECT COUNT(*) as count FROM shortbow_symptom_links")
                total_links = cursor.fetchone()["count"]

                # Count calculations
                cursor = thread_conn.execute("SELECT COUNT(*) as count FROM shortbow_calculations")
                total_calculations = cursor.fetchone()["count"]

                # Count saved calculations
                cursor = thread_conn.execute(
                    "SELECT COUNT(*) as count FROM shortbow_calculations WHERE saved = 1"
                )
                saved_calculations = cursor.fetchone()["count"]

                return total_symptoms, total_links, total_calculations, saved_calculations
            finally:
                thread_conn.close()

        # Get all stats
        (
            total_symptoms,
            total_links,
            total_calculations,
            saved_calculations,
        ) = await anyio.to_thread.run_sync(_get_stats)

        return ShortBowStats(
            total_symptoms=total_symptoms,
            total_links=total_links,
            total_calculations=total_calculations,
            saved_calculations=saved_calculations,
        )

    except Exception as e:
        logger.error(f"Stats failed: {e}")
        raise HTTPException(status_code=500, detail=f"Stats failed: {e}")


@router.post("/calculations", response_model=CalculationResponse)
async def create_calculation(
    request: CalculationRequest, conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Create a new calculation record."""
    try:
        import json

        def _create_calculation():
            cursor = conn.execute(
                "INSERT INTO shortbow_calculations (initial_symptom, selected_symptoms) VALUES (?, ?)",
                (request.initial_symptom, json.dumps(request.selected_symptoms)),
            )
            conn.commit()

            # Get the created record
            cursor = conn.execute(
                "SELECT id, calculation_date, initial_symptom, selected_symptoms, saved, created_at FROM shortbow_calculations WHERE id = ?",
                (cursor.lastrowid,),
            )
            return cursor.fetchone()

        row = await anyio.to_thread.run_sync(_create_calculation)

        return CalculationResponse(
            id=row["id"],
            calculation_date=row["calculation_date"],
            initial_symptom=row["initial_symptom"],
            selected_symptoms=json.loads(row["selected_symptoms"]),
            saved=bool(row["saved"]),
            created_at=row["created_at"],
        )

    except Exception as e:
        logger.error(f"Create calculation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Create calculation failed: {e}")


@router.get("/calculations", response_model=list[CalculationResponse])
async def get_calculations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    conn: sqlite3.Connection = Depends(get_db_connection),
):
    """Get list of calculations."""
    try:

        def _get_calculations():
            cursor = conn.execute(
                "SELECT id, calculation_date, initial_symptom, selected_symptoms, saved, created_at FROM shortbow_calculations ORDER BY calculation_date DESC LIMIT ? OFFSET ?",
                (limit, offset),
            )
            return cursor.fetchall()

        calculations = await anyio.to_thread.run_sync(_get_calculations)

        import json

        return [
            CalculationResponse(
                id=row["id"],
                calculation_date=row["calculation_date"],
                initial_symptom=row["initial_symptom"],
                selected_symptoms=json.loads(row["selected_symptoms"]),
                saved=bool(row["saved"]),
                created_at=row["created_at"],
            )
            for row in calculations
        ]

    except Exception as e:
        logger.error(f"Get calculations failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get calculations failed: {e}")


@router.get("/calculations/{calculation_id}", response_model=CalculationResponse)
async def get_calculation(
    calculation_id: int, conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Get specific calculation."""
    try:

        def _get_calculation():
            cursor = conn.execute(
                "SELECT id, calculation_date, initial_symptom, selected_symptoms, saved, created_at FROM shortbow_calculations WHERE id = ?",
                (calculation_id,),
            )
            return cursor.fetchone()

        row = await anyio.to_thread.run_sync(_get_calculation)

        if not row:
            raise HTTPException(status_code=404, detail="Calculation not found")

        import json

        return CalculationResponse(
            id=row["id"],
            calculation_date=row["calculation_date"],
            initial_symptom=row["initial_symptom"],
            selected_symptoms=json.loads(row["selected_symptoms"]),
            saved=bool(row["saved"]),
            created_at=row["created_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get calculation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Get calculation failed: {e}")


@router.post("/calculations/{calculation_id}/save")
async def save_calculation(
    calculation_id: int, conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Save a calculation."""
    try:

        def _save_calculation():
            cursor = conn.execute(
                "UPDATE shortbow_calculations SET saved = 1 WHERE id = ?", (calculation_id,)
            )
            conn.commit()
            return cursor.rowcount

        rowcount = await anyio.to_thread.run_sync(_save_calculation)

        if rowcount == 0:
            raise HTTPException(status_code=404, detail="Calculation not found")

        return {"success": True, "message": "Calculation saved"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Save calculation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Save calculation failed: {e}")


@router.post("/create-decision-tree")
async def create_decision_tree(
    symptoms: list[str], conn: sqlite3.Connection = Depends(get_db_connection)
):
    """Create a hierarchical decision tree from symptom path."""
    try:
        if not symptoms:
            raise HTTPException(status_code=422, detail="No symptoms provided")

        def _create_hierarchical_tree():
            # Create root node with first symptom
            cursor = conn.execute(
                "INSERT INTO nodes (parent_id, depth, slot, label) VALUES (NULL, 0, NULL, ?)",
                (symptoms[0],),
            )
            root_id = cursor.lastrowid

            current_parent_id = root_id

            # Add subsequent symptoms as children (drilling down)
            for i in range(1, len(symptoms)):
                # Get current parent depth
                cursor = conn.execute("SELECT depth FROM nodes WHERE id = ?", (current_parent_id,))
                parent_depth = cursor.fetchone()[0]

                if parent_depth >= 6:
                    break  # Max depth reached

                # Check if parent already has 5 children
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM nodes WHERE parent_id = ?", (current_parent_id,)
                )
                child_count = cursor.fetchone()[0]

                if child_count >= 5:
                    break  # Max children reached

                # Find next available slot
                cursor = conn.execute(
                    "SELECT MAX(slot) FROM nodes WHERE parent_id = ?", (current_parent_id,)
                )
                max_slot = cursor.fetchone()[0]
                next_slot = (max_slot or 0) + 1

                # Insert new child
                cursor = conn.execute(
                    "INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?, ?, ?, ?)",
                    (current_parent_id, parent_depth + 1, next_slot, symptoms[i]),
                )

                # Update current parent to be the newly created child
                current_parent_id = cursor.lastrowid

            conn.commit()
            return root_id, current_parent_id

        root_id, final_node_id = await anyio.to_thread.run_sync(_create_hierarchical_tree)

        return {
            "success": True,
            "root_id": root_id,
            "final_node_id": final_node_id,
            "symptoms_created": len(symptoms),
            "message": f"Decision tree created with {len(symptoms)} symptoms",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create decision tree failed: {e}")
        raise HTTPException(status_code=500, detail=f"Create decision tree failed: {e}")
