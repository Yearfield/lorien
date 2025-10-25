"""
Data ingestion for EngineShortBow symptom matrix files.
"""

import logging

import pandas as pd

from .utils import normalize_symptom_name, validate_probability

logger = logging.getLogger(__name__)


def extract_symptom_matrix(file_path: str) -> tuple[list[str], dict[tuple[str, str], float]]:
    """
    Extract symptom matrix from Excel file.

    Args:
        file_path: Path to Excel file

    Returns:
        Tuple of (symptom_names, symptom_links) where symptom_links is a dict
        mapping (from_symptom, to_symptom) -> probability

    Raises:
        ValueError: If file format is invalid or data is malformed
    """
    try:
        # Read Excel file
        df = pd.read_excel(file_path, index_col=0)

        # Get symptom names from index and columns
        symptoms = list(df.index)

        # Validate that index and columns match (square matrix)
        if list(df.columns) != symptoms:
            logger.warning("Matrix is not square - using row indices as symptom names")

        # Normalize symptom names
        normalized_symptoms = [normalize_symptom_name(s) for s in symptoms]

        # Extract symptom links
        symptom_links = {}

        for from_symptom in symptoms:
            from_normalized = normalize_symptom_name(from_symptom)

            for to_symptom in symptoms:
                to_normalized = normalize_symptom_name(to_symptom)

                # Skip self-links (diagonal)
                if from_symptom == to_symptom:
                    continue

                # Get probability value
                try:
                    probability = float(df.loc[from_symptom, to_symptom])

                    # Validate probability
                    if not validate_probability(probability):
                        logger.warning(
                            f"Invalid probability {probability} for {from_symptom} -> {to_symptom}"
                        )
                        continue

                    # Only store non-zero probabilities
                    if probability > 0:
                        symptom_links[(from_normalized, to_normalized)] = probability

                except (ValueError, KeyError) as e:
                    logger.warning(
                        f"Could not extract probability for {from_symptom} -> {to_symptom}: {e}"
                    )
                    continue

        logger.info(f"Extracted {len(symptoms)} symptoms with {len(symptom_links)} links")
        return normalized_symptoms, symptom_links

    except Exception as e:
        raise ValueError(f"Failed to extract symptom matrix from {file_path}: {e}")


def ingest_file(file_path: str) -> tuple[list[str], dict[tuple[str, str], float]]:
    """
    Ingest symptom matrix file and return extracted data.

    Args:
        file_path: Path to Excel file

    Returns:
        Tuple of (symptom_names, symptom_links)
    """
    return extract_symptom_matrix(file_path)
