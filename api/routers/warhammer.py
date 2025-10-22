"""
Warhammer API router for EngineWarhammer.
Provides CRUD operations, import functionality, and calculation endpoints for Bayesian disease probability calculations.
"""

import logging
import os
import sqlite3
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from pydantic import BaseModel

from api.settings import get_db_path
from Engines.EngineWarhammer import (
    apply_import,
    ingest_file,
)
from Engines.EngineWarhammer.calculator import calculate_disease_probabilities_from_db
from Engines.EngineWarhammer.store import (
    get_calculation,
    list_calculations,
)
from Engines.EngineWarhammer.utils import normalize_symptom_name

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/warhammer", tags=["warhammer"])


# Pydantic models for request/response
class SymptomResponse(BaseModel):
    id: int
    symptom_name: str
    probability: float
    created_at: str
    updated_at: str


class DiseaseResponse(BaseModel):
    id: int
    disease_name: str
    estimated_lifetime_risk: float
    created_at: str
    updated_at: str


class DiseaseResult(BaseModel):
    disease: str
    probability: float


class CalculationRequest(BaseModel):
    symptoms: list[str]


class CalculationResponse(BaseModel):
    calculation_id: Optional[int] = None
    input_symptoms: list[str]
    results: list[DiseaseResult]
    timestamp: str
    errors: list[str] = []
    synonym_resolutions: list[dict] = []  # Maps original -> resolved symptom
    explanations: list[dict] = []  # Prior and per-symptom factors per disease


class ImportResultResponse(BaseModel):
    success: bool
    diseases_processed: int = 0
    diseases_created: int = 0
    diseases_updated: int = 0
    symptoms_processed: int = 0
    symptoms_created: int = 0
    symptoms_updated: int = 0
    conditionals_processed: int = 0
    conditionals_created: int = 0
    conditionals_updated: int = 0
    errors: list[str] = []
    warnings: list[str] = []


class WarhammerStats(BaseModel):
    total_diseases: int
    total_symptoms: int
    total_conditionals: int
    total_calculations: int
    saved_calculations: int


class SavedCalculation(BaseModel):
    id: int
    calculation_date: str
    input_symptoms: list[str]
    results: list[DiseaseResult]
    saved: bool


# Dependency to get database path
def get_database_path() -> str:
    """Get the database path."""
    return get_db_path()


@router.get("/symptoms", response_model=list[SymptomResponse])
async def list_symptoms(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of symptoms to return"),
    offset: int = Query(0, ge=0, description="Number of symptoms to skip"),
    search: Optional[str] = Query(None, description="Search term for symptom name"),
    db_path: str = Depends(get_database_path),
):
    """List symptoms with optional search and pagination."""
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Build query with optional search
        query = "SELECT * FROM symptoms"
        params = []

        if search:
            query += " WHERE symptom_name LIKE ?"
            params.append(f"%{search}%")

        query += " ORDER BY symptom_name LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [SymptomResponse(**dict(row)) for row in rows]


@router.get("/diseases", response_model=list[DiseaseResponse])
async def list_diseases(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of diseases to return"),
    offset: int = Query(0, ge=0, description="Number of diseases to skip"),
    search: Optional[str] = Query(None, description="Search term for disease name"),
    db_path: str = Depends(get_database_path),
):
    """List diseases with optional search and pagination."""
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Build query with optional search
        query = "SELECT * FROM diseases"
        params = []

        if search:
            query += " WHERE disease_name LIKE ?"
            params.append(f"%{search}%")

        query += " ORDER BY disease_name LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [DiseaseResponse(**dict(row)) for row in rows]


@router.post("/calculate", response_model=CalculationResponse)
async def calculate_disease_probabilities(
    request: CalculationRequest,
    db_path: str = Depends(get_database_path),
):
    """Calculate disease probabilities based on observed symptoms."""
    import sqlite3
    from datetime import datetime

    # Validate symptoms
    if not request.symptoms:
        raise HTTPException(status_code=400, detail="No symptoms provided")

    if len(request.symptoms) < 1 or len(request.symptoms) > 5:
        raise HTTPException(status_code=400, detail="Must provide 1-5 symptoms")

    try:
        with sqlite3.connect(db_path) as conn:
            # Perform calculation
            result = calculate_disease_probabilities_from_db(request.symptoms, db_path)

            # Convert results to response format
            disease_results = [
                DiseaseResult(disease=r.disease_name, probability=r.probability)
                for r in result.results
            ]

            return CalculationResponse(
                input_symptoms=result.input_symptoms,
                results=disease_results,
                timestamp=datetime.utcnow().isoformat() + "Z",
                errors=result.errors,
                synonym_resolutions=result.synonym_resolutions,
                explanations=result.explanations,
            )

    except Exception as e:
        logger.error(f"Calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Calculation failed: {str(e)}")


@router.post("/calculations/{calculation_id}/save")
async def save_calculation_result(
    calculation_id: int,
    db_path: str = Depends(get_database_path),
):
    """Save a calculation result for future reference."""
    import sqlite3

    try:
        with sqlite3.connect(db_path) as conn:
            # Get the calculation
            calculation = get_calculation(db_path, calculation_id)
            if not calculation:
                raise HTTPException(status_code=404, detail="Calculation not found")

            # Mark as saved
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE warhammer_calculations SET saved = 1 WHERE id = ?", (calculation_id,)
            )
            conn.commit()

            return {"message": "Calculation saved successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save calculation: {str(e)}")


@router.get("/calculations", response_model=list[SavedCalculation])
async def list_saved_calculations(
    limit: int = Query(50, ge=1, le=100, description="Maximum number of calculations to return"),
    offset: int = Query(0, ge=0, description="Number of calculations to skip"),
    db_path: str = Depends(get_database_path),
):
    """List saved calculations."""
    try:
        calculations = list_calculations(db_path, limit, offset)

        return [
            SavedCalculation(
                id=calc["id"],
                calculation_date=calc["calculation_date"],
                input_symptoms=calc["input_symptoms"],
                results=[
                    DiseaseResult(disease=r["disease"], probability=r["probability"])
                    for r in calc["results"]
                ],
                saved=calc["saved"],
            )
            for calc in calculations
        ]

    except Exception as e:
        logger.error(f"Failed to list calculations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list calculations: {str(e)}")


@router.get("/calculations/{calculation_id}", response_model=SavedCalculation)
async def get_saved_calculation(
    calculation_id: int,
    db_path: str = Depends(get_database_path),
):
    """Get a specific saved calculation."""
    try:
        calculation = get_calculation(db_path, calculation_id)
        if not calculation:
            raise HTTPException(status_code=404, detail="Calculation not found")

        return SavedCalculation(
            id=calculation["id"],
            calculation_date=calculation["calculation_date"],
            input_symptoms=calculation["input_symptoms"],
            results=[
                DiseaseResult(disease=r["disease"], probability=r["probability"])
                for r in calculation["results"]
            ],
            saved=calculation["saved"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get calculation: {str(e)}")


@router.post("/import/diseases", response_model=ImportResultResponse)
async def import_diseases(
    file: UploadFile = File(..., description="CSV or XLSX file containing disease data"),
    db_path: str = Depends(get_database_path),
):
    """Import disease data from a spreadsheet file."""

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
        logger.info(f"Importing disease file: {file.filename}")
        ingested_data = ingest_file(file_content, file.filename, "diseases")

        if not ingested_data["success"]:
            return ImportResultResponse(
                success=False,
                errors=ingested_data.get("errors", []),
            )

        # Apply import to database
        result = apply_import(db_path, ingested_data, "diseases")

        logger.info(
            f"Disease import completed: {result.diseases_processed} diseases processed, "
            f"{result.diseases_created} created, {result.diseases_updated} updated"
        )

        return ImportResultResponse(
            success=len(result.errors) == 0,
            diseases_processed=result.diseases_processed,
            diseases_created=result.diseases_created,
            diseases_updated=result.diseases_updated,
            errors=result.errors,
            warnings=result.warnings,
        )

    except Exception as e:
        logger.error(f"Disease import failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/import/symptoms", response_model=ImportResultResponse)
async def import_symptoms(
    file: UploadFile = File(..., description="CSV or XLSX file containing symptom data"),
    db_path: str = Depends(get_database_path),
):
    """Import symptom data from a spreadsheet file."""

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
        logger.info(f"Importing symptom file: {file.filename}")
        ingested_data = ingest_file(file_content, file.filename, "symptoms")

        if not ingested_data["success"]:
            return ImportResultResponse(
                success=False,
                errors=ingested_data.get("errors", []),
            )

        # Apply import to database
        result = apply_import(db_path, ingested_data, "symptoms")

        logger.info(
            f"Symptom import completed: {result.symptoms_processed} symptoms processed, "
            f"{result.symptoms_created} created, {result.symptoms_updated} updated"
        )

        return ImportResultResponse(
            success=len(result.errors) == 0,
            symptoms_processed=result.symptoms_processed,
            symptoms_created=result.symptoms_created,
            symptoms_updated=result.symptoms_updated,
            errors=result.errors,
            warnings=result.warnings,
        )

    except Exception as e:
        logger.error(f"Symptom import failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.post("/import/conditionals", response_model=ImportResultResponse)
async def import_conditionals(
    file: UploadFile = File(
        ..., description="CSV or XLSX file containing conditional probability data"
    ),
    db_path: str = Depends(get_database_path),
):
    """Import conditional probability data from a spreadsheet file."""

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
        logger.info(f"Importing conditional file: {file.filename}")
        ingested_data = ingest_file(file_content, file.filename, "conditionals")

        if not ingested_data["success"]:
            return ImportResultResponse(
                success=False,
                errors=ingested_data.get("errors", []),
            )

        # Apply import to database
        result = apply_import(db_path, ingested_data, "conditionals")

        logger.info(
            f"Conditional import completed: {result.conditionals_processed} conditionals processed, "
            f"{result.conditionals_created} created, {result.conditionals_updated} updated"
        )

        return ImportResultResponse(
            success=len(result.errors) == 0,
            conditionals_processed=result.conditionals_processed,
            conditionals_created=result.conditionals_created,
            conditionals_updated=result.conditionals_updated,
            errors=result.errors,
            warnings=result.warnings,
        )

    except Exception as e:
        logger.error(f"Conditional import failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")


@router.get("/stats/summary", response_model=WarhammerStats)
async def get_warhammer_stats(db_path: str = Depends(get_database_path)):
    """Get summary statistics about Warhammer data."""
    import sqlite3

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get disease count
        cursor.execute("SELECT COUNT(*) FROM diseases")
        disease_count = cursor.fetchone()[0]

        # Get symptom count
        cursor.execute("SELECT COUNT(*) FROM symptoms")
        symptom_count = cursor.fetchone()[0]

        # Get conditional count
        cursor.execute("SELECT COUNT(*) FROM symptom_disease_conditionals")
        conditional_count = cursor.fetchone()[0]

        # Get total calculations count
        cursor.execute("SELECT COUNT(*) FROM warhammer_calculations")
        total_calculations = cursor.fetchone()[0]

        # Get saved calculations count
        cursor.execute("SELECT COUNT(*) FROM warhammer_calculations WHERE saved = 1")
        saved_calculations = cursor.fetchone()[0]

        return WarhammerStats(
            total_diseases=disease_count,
            total_symptoms=symptom_count,
            total_conditionals=conditional_count,
            total_calculations=total_calculations,
            saved_calculations=saved_calculations,
        )


class SymptomComparisonResponse(BaseModel):
    """Response model for symptom comparison."""

    decision_tree_symptoms: list[str]
    warhammer_symptoms: list[str]
    matching_symptoms: list[str]
    missing_from_warhammer: list[str]
    extra_in_warhammer: list[str]
    total_decision_tree: int
    total_warhammer: int
    match_count: int
    normalized_matches: list[dict]  # Show which symptoms were matched through normalization


class SymptomSynonym(BaseModel):
    """Model for symptom synonym mapping."""

    id: int
    warhammer_symptom: str
    decision_tree_symptom: str
    created_at: str
    updated_at: str


class CreateSynonymRequest(BaseModel):
    """Request model for creating a symptom synonym."""

    warhammer_symptom: str
    decision_tree_symptom: str


@router.get("/symptoms/comparison", response_model=SymptomComparisonResponse)
async def compare_symptoms(db_path: str = Depends(get_database_path)):
    """Compare decision tree symptoms with Warhammer database symptoms."""
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Get all decision tree symptoms (roots + all children)
            decision_tree_symptoms = set()

            # Get all nodes (roots and children)
            nodes_cursor = conn.execute("SELECT label FROM nodes")
            nodes = [row["label"] for row in nodes_cursor.fetchall()]
            decision_tree_symptoms.update(nodes)

            # Get Warhammer symptoms
            warhammer_cursor = conn.execute("SELECT symptom_name FROM symptoms")
            warhammer_symptoms = set(row["symptom_name"] for row in warhammer_cursor.fetchall())

            # Normalize symptom names for better matching
            def normalize_symptom_name(name):
                """Normalize symptom name for comparison."""
                return name.lower().strip()

            # Create normalized mappings
            decision_tree_normalized = {
                normalize_symptom_name(symptom): symptom for symptom in decision_tree_symptoms
            }
            warhammer_normalized = {
                normalize_symptom_name(symptom): symptom for symptom in warhammer_symptoms
            }

            # Find exact matches (case-insensitive, whitespace-normalized)
            normalized_decision_tree = set(decision_tree_normalized.keys())
            normalized_warhammer = set(warhammer_normalized.keys())

            # Find normalized matches
            normalized_matching = normalized_decision_tree.intersection(normalized_warhammer)

            # Convert back to original names for exact matches and create normalized match info
            exact_matching = []
            normalized_matches_info = []
            for normalized_name in normalized_matching:
                decision_tree_original = decision_tree_normalized[normalized_name]
                warhammer_original = warhammer_normalized[normalized_name]
                exact_matching.append(decision_tree_original)

                # Only include in normalized matches if the original names are different
                if decision_tree_original != warhammer_original:
                    normalized_matches_info.append(
                        {
                            "decision_tree": decision_tree_original,
                            "warhammer": warhammer_original,
                            "normalized": normalized_name,
                        }
                    )

            # Get synonym mappings and add them to matching symptoms
            synonym_cursor = conn.execute(
                """
                SELECT warhammer_symptom, decision_tree_symptom
                FROM symptom_synonyms
            """
            )
            synonym_mappings = {row[1]: row[0] for row in synonym_cursor.fetchall()}

            # Add synonym-based matches
            synonym_matches = []
            for decision_tree_symptom, warhammer_symptom in synonym_mappings.items():
                # Check if both symptoms exist in their respective databases
                if (
                    decision_tree_symptom in decision_tree_symptoms
                    and warhammer_symptom in warhammer_symptoms
                ):
                    synonym_matches.append(decision_tree_symptom)

            # Combine exact matches and synonym matches (remove duplicates)
            all_matching = list(set(exact_matching + synonym_matches))

            # Find symptoms that exist in decision tree but not in warhammer (even after normalization and synonyms)
            missing_from_warhammer = []
            for symptom in decision_tree_symptoms:
                normalized_symptom = normalize_symptom_name(symptom)
                # Check if symptom is matched through normalization OR synonyms
                is_normalized_match = normalized_symptom in normalized_warhammer
                is_synonym_match = symptom in synonym_mappings

                if not is_normalized_match and not is_synonym_match:
                    missing_from_warhammer.append(symptom)

            # Find symptoms that exist in warhammer but not in decision tree (even after normalization and synonyms)
            # Exclude symptoms that are already handled by normalization or synonyms
            extra_in_warhammer = []
            for symptom in warhammer_symptoms:
                normalized_symptom = normalize_symptom_name(symptom)
                # Check if symptom is matched through normalization OR synonyms
                is_normalized_match = normalized_symptom in normalized_decision_tree
                is_synonym_match = symptom in synonym_mappings.values()

                # Also check if this symptom is already matched through normalization in the normalized_matches_info
                is_already_normalized = any(
                    normalize_symptom_name(match["warhammer"]) == normalized_symptom
                    for match in normalized_matches_info
                )

                if not is_normalized_match and not is_synonym_match and not is_already_normalized:
                    extra_in_warhammer.append(symptom)

            # Sort the results
            decision_tree_list = sorted(list(decision_tree_symptoms))
            warhammer_list = sorted(list(warhammer_symptoms))
            matching = sorted(all_matching)
            missing_from_warhammer = sorted(missing_from_warhammer)
            extra_in_warhammer = sorted(extra_in_warhammer)

            return SymptomComparisonResponse(
                decision_tree_symptoms=decision_tree_list,
                warhammer_symptoms=warhammer_list,
                matching_symptoms=matching,
                missing_from_warhammer=missing_from_warhammer,
                extra_in_warhammer=extra_in_warhammer,
                total_decision_tree=len(decision_tree_list),
                total_warhammer=len(warhammer_list),
                match_count=len(matching),
                normalized_matches=normalized_matches_info,
            )

    except Exception as e:
        logger.error(f"Error comparing symptoms: {e}")
        raise HTTPException(status_code=500, detail=f"Error comparing symptoms: {str(e)}")


@router.get("/synonyms", response_model=list[SymptomSynonym])
async def list_synonyms(db_path: str = Depends(get_database_path)):
    """List all symptom synonym mappings."""
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                """
                SELECT id, warhammer_symptom, decision_tree_symptom, created_at, updated_at
                FROM symptom_synonyms
                ORDER BY created_at DESC
            """
            )
            rows = cursor.fetchall()

            return [
                SymptomSynonym(
                    id=row[0],
                    warhammer_symptom=row[1],
                    decision_tree_symptom=row[2],
                    created_at=row[3],
                    updated_at=row[4],
                )
                for row in rows
            ]

    except Exception as e:
        logger.error(f"Error listing synonyms: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing synonyms: {str(e)}")


@router.post("/synonyms", response_model=SymptomSynonym)
async def create_synonym(request: CreateSynonymRequest, db_path: str = Depends(get_database_path)):
    """Create a new symptom synonym mapping."""
    try:
        # Validate that this isn't just a case-only difference
        if normalize_symptom_name(request.warhammer_symptom) == normalize_symptom_name(
            request.decision_tree_symptom
        ):
            raise HTTPException(
                status_code=400,
                detail="Cannot create synonym for case-only differences. These are handled automatically by normalization.",
            )

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check if synonym already exists
            cursor.execute(
                """
                SELECT id FROM symptom_synonyms
                WHERE warhammer_symptom = ? AND decision_tree_symptom = ?
            """,
                (request.warhammer_symptom, request.decision_tree_symptom),
            )

            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Synonym mapping already exists")

            # Create new synonym
            cursor.execute(
                """
                INSERT INTO symptom_synonyms (warhammer_symptom, decision_tree_symptom)
                VALUES (?, ?)
            """,
                (request.warhammer_symptom, request.decision_tree_symptom),
            )

            synonym_id = cursor.lastrowid
            conn.commit()

            # Fetch the created synonym
            cursor.execute(
                """
                SELECT id, warhammer_symptom, decision_tree_symptom, created_at, updated_at
                FROM symptom_synonyms WHERE id = ?
            """,
                (synonym_id,),
            )

            row = cursor.fetchone()
            return SymptomSynonym(
                id=row[0],
                warhammer_symptom=row[1],
                decision_tree_symptom=row[2],
                created_at=row[3],
                updated_at=row[4],
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating synonym: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating synonym: {str(e)}")


@router.delete("/synonyms/{synonym_id}")
async def delete_synonym(synonym_id: int, db_path: str = Depends(get_database_path)):
    """Delete a symptom synonym mapping."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check if synonym exists
            cursor.execute("SELECT id FROM symptom_synonyms WHERE id = ?", (synonym_id,))
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail="Synonym not found")

            # Delete the synonym
            cursor.execute("DELETE FROM symptom_synonyms WHERE id = ?", (synonym_id,))
            conn.commit()

            return {"message": "Synonym deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting synonym: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting synonym: {str(e)}")
