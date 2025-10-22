"""
Core Bayesian calculation logic for EngineWarhammer.
Implements disease probability calculations based on observed symptoms.
"""

import logging
import sqlite3
from dataclasses import dataclass
from typing import Optional

from .utils import normalize_symptom_name, validate_symptom_list

logger = logging.getLogger(__name__)


@dataclass
class DiseaseResult:
    """Result for a single disease probability calculation."""

    disease_name: str
    probability: float


@dataclass
class WarhammerCalculationResult:
    """Complete result of a Warhammer calculation."""

    input_symptoms: list[str]
    results: list[DiseaseResult]
    calculation_id: Optional[int] = None
    timestamp: Optional[str] = None
    errors: list[str] = None
    synonym_resolutions: list[dict[str, str]] = None  # Maps original -> resolved symptom
    explanations: list[dict] = None  # Per-disease explanation: prior and P(S|D)

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.synonym_resolutions is None:
            self.synonym_resolutions = []
        if self.explanations is None:
            self.explanations = []


def calculate_disease_probabilities_from_db(
    symptoms: list[str], db_path: str
) -> WarhammerCalculationResult:
    """
    Calculate disease probabilities using Bayesian inference from database.
    Resolves synonyms for symptoms not found in Warhammer database.

    Args:
        symptoms: List of observed symptom names (1-5 symptoms)
        db_path: Path to the SQLite database

    Returns:
        WarhammerCalculationResult with top 5 diseases and probabilities
    """
    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Resolve synonyms for symptoms not in Warhammer database
            resolved_symptoms, synonym_resolutions = _resolve_symptom_synonyms(symptoms, conn)

            # Fetch disease data
            disease_cursor = conn.execute(
                "SELECT disease_name, estimated_lifetime_risk FROM diseases"
            )
            disease_data = [dict(row) for row in disease_cursor.fetchall()]

            # Fetch symptom data
            symptom_cursor = conn.execute("SELECT symptom_name, probability FROM symptoms")
            symptom_data = [dict(row) for row in symptom_cursor.fetchall()]

            # Fetch conditional data
            conditional_cursor = conn.execute(
                """
                SELECT s.symptom_name, d.disease_name, c.conditional_probability
                FROM symptom_disease_conditionals c
                JOIN symptoms s ON c.symptom_id = s.id
                JOIN diseases d ON c.disease_id = d.id
            """
            )
            conditional_data = [dict(row) for row in conditional_cursor.fetchall()]

            # Call the main calculation function with resolved symptoms
            result = calculate_disease_probabilities(
                resolved_symptoms, disease_data, symptom_data, conditional_data
            )
            result.synonym_resolutions = synonym_resolutions
            return result

    except Exception as e:
        logger.error(f"Database error during calculation: {e}")
        return WarhammerCalculationResult(
            input_symptoms=symptoms, results=[], errors=[f"Database error: {str(e)}"]
        )


def calculate_disease_probabilities(
    symptoms: list[str],
    disease_data: list[dict],
    symptom_data: list[dict],
    conditional_data: list[dict],
) -> WarhammerCalculationResult:
    """
    Calculate disease probabilities using Bayesian inference.

    Args:
        symptoms: List of observed symptom names (1-5 symptoms)
        disease_data: List of disease dictionaries with name and lifetime risk
        symptom_data: List of symptom dictionaries with name and probability
        conditional_data: List of conditional probability dictionaries

    Returns:
        WarhammerCalculationResult with top 5 diseases and probabilities
    """
    # Validate input symptoms
    is_valid, error_msg = validate_symptom_list(symptoms)
    if not is_valid:
        return WarhammerCalculationResult(input_symptoms=symptoms, results=[], errors=[error_msg])

    # Normalize symptoms for lookup
    normalized_symptoms = [s.strip().lower() for s in symptoms]

    # Build lookup dictionaries
    disease_probs = {row["disease_name"]: row["estimated_lifetime_risk"] for row in disease_data}

    symptom_probs = {row["symptom_name"]: row["probability"] for row in symptom_data}

    symptom_given_disease = {
        (row["symptom_name"], row["disease_name"]): row["conditional_probability"]
        for row in conditional_data
    }

    # Calculate unnormalized scores for each disease
    scores = []
    missing_data_diseases = []

    for disease_name, prob_vm in disease_probs.items():
        p_symptoms_given_vm = []
        missing_data = False

        for symptom in normalized_symptoms:
            key = (symptom, disease_name)
            prob = symptom_given_disease.get(key)

            if prob is not None:
                p_symptoms_given_vm.append(prob)
            else:
                missing_data = True
                break

        if missing_data:
            missing_data_diseases.append(disease_name)
            continue

        # Calculate unnormalized score: P(Disease) * Π P(Symptom|Disease)
        score = prob_vm
        for p in p_symptoms_given_vm:
            score *= p

        scores.append((disease_name, score))

    # Handle missing data warnings
    errors = []
    if missing_data_diseases:
        errors.append(
            f"Missing conditional probability data for {len(missing_data_diseases)} diseases"
        )
        logger.warning(f"Missing data for diseases: {missing_data_diseases[:5]}...")

    if not scores:
        errors.append("No diseases could be calculated due to missing conditional probability data")
        return WarhammerCalculationResult(input_symptoms=symptoms, results=[], errors=errors)

    # Normalize scores to probabilities
    total_score = sum(score for _, score in scores)
    if total_score == 0:
        errors.append("All disease scores are zero - check data quality")
        return WarhammerCalculationResult(input_symptoms=symptoms, results=[], errors=errors)

    # Create normalized results
    normalized_results = [
        DiseaseResult(disease_name=disease, probability=score / total_score)
        for disease, score in scores
    ]

    # Sort by probability (descending) and take top 5
    top_results = sorted(normalized_results, key=lambda x: x.probability, reverse=True)[:5]

    # Build explanations for top results
    explanations = []
    top_disease_names = {r.disease_name for r in top_results}
    for disease in top_disease_names:
        factors = []
        for symptom in normalized_symptoms:
            val = symptom_given_disease.get((symptom, disease))
            if val is not None:
                factors.append({"symptom": symptom, "p_symptom_given_disease": val})
        explanations.append(
            {
                "disease": disease,
                "prior": disease_probs.get(disease, 0.0),
                "factors": factors,
            }
        )

    return WarhammerCalculationResult(
        input_symptoms=symptoms,
        results=top_results,
        errors=errors,
        explanations=explanations,
    )


def calculate_from_database(symptoms: list[str], db_connection) -> WarhammerCalculationResult:
    """
    Calculate disease probabilities using data from database.

    Args:
        symptoms: List of observed symptom names
        db_connection: Database connection object

    Returns:
        WarhammerCalculationResult with calculation results
    """
    try:
        # Fetch disease data
        disease_cursor = db_connection.execute(
            "SELECT disease_name, estimated_lifetime_risk FROM diseases"
        )
        disease_data = [
            {"disease_name": row[0], "estimated_lifetime_risk": row[1]}
            for row in disease_cursor.fetchall()
        ]

        # Fetch symptom data
        symptom_cursor = db_connection.execute("SELECT symptom_name, probability FROM symptoms")
        symptom_data = [
            {"symptom_name": row[0], "probability": row[1]} for row in symptom_cursor.fetchall()
        ]

        # Fetch conditional probability data
        conditional_cursor = db_connection.execute(
            """
            SELECT s.symptom_name, d.disease_name, sdc.conditional_probability
            FROM symptom_disease_conditionals sdc
            JOIN symptoms s ON sdc.symptom_id = s.id
            JOIN diseases d ON sdc.disease_id = d.id
            """
        )
        conditional_data = [
            {"symptom_name": row[0], "disease_name": row[1], "conditional_probability": row[2]}
            for row in conditional_cursor.fetchall()
        ]

        return calculate_disease_probabilities(
            symptoms, disease_data, symptom_data, conditional_data
        )

    except Exception as e:
        logger.error(f"Error calculating from database: {str(e)}")
        return WarhammerCalculationResult(
            input_symptoms=symptoms, results=[], errors=[f"Database error: {str(e)}"]
        )


def _resolve_symptom_synonyms(
    symptoms: list[str], conn: sqlite3.Connection
) -> tuple[list[str], list[dict[str, str]]]:
    """
    Resolve synonyms for symptoms that are not in the Warhammer database.

    Args:
        symptoms: List of input symptom names
        conn: Database connection

    Returns:
        Tuple of (resolved_symptoms, synonym_resolutions)
        - resolved_symptoms: List of resolved symptom names (original or synonym)
        - synonym_resolutions: List of dicts mapping original -> resolved symptom
    """
    resolved_symptoms = []
    synonym_resolutions = []

    # Get all Warhammer symptoms for lookup
    warhammer_cursor = conn.execute("SELECT symptom_name FROM symptoms")
    warhammer_symptoms = {row[0].lower().strip() for row in warhammer_cursor.fetchall()}

    # Get all synonym mappings
    synonym_cursor = conn.execute(
        """
        SELECT warhammer_symptom, decision_tree_symptom
        FROM symptom_synonyms
    """
    )
    synonym_mappings = {row[1]: row[0] for row in synonym_cursor.fetchall()}

    for symptom in symptoms:
        normalized_symptom = normalize_symptom_name(symptom)

        # Check if symptom exists in Warhammer database
        if normalized_symptom in warhammer_symptoms:
            # Use original symptom name from Warhammer database
            warhammer_cursor = conn.execute(
                "SELECT symptom_name FROM symptoms WHERE LOWER(TRIM(symptom_name)) = ?",
                (normalized_symptom,),
            )
            warhammer_symptom = warhammer_cursor.fetchone()
            if warhammer_symptom:
                resolved_symptom = warhammer_symptom[0]
                resolved_symptoms.append(resolved_symptom)
                if symptom != resolved_symptom:
                    synonym_resolutions.append({"original": symptom, "resolved": resolved_symptom})
            else:
                resolved_symptoms.append(symptom)  # Fallback to original
        else:
            # Check if symptom has a synonym mapping
            if symptom in synonym_mappings:
                warhammer_synonym = synonym_mappings[symptom]
                # Verify the synonym exists in Warhammer database
                warhammer_cursor = conn.execute(
                    "SELECT symptom_name FROM symptoms WHERE LOWER(TRIM(symptom_name)) = ?",
                    (normalize_symptom_name(warhammer_synonym),),
                )
                warhammer_symptom = warhammer_cursor.fetchone()
                if warhammer_symptom:
                    resolved_symptom = warhammer_symptom[0]
                    resolved_symptoms.append(resolved_symptom)
                    synonym_resolutions.append({"original": symptom, "resolved": resolved_symptom})
                    logger.info(f"Resolved synonym: '{symptom}' -> '{resolved_symptom}'")
                else:
                    resolved_symptoms.append(symptom)  # Fallback to original
            else:
                # No synonym found, use original symptom
                resolved_symptoms.append(symptom)
                logger.warning(f"No Warhammer data or synonym found for symptom: '{symptom}'")

    return resolved_symptoms, synonym_resolutions
