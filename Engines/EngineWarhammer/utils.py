"""
Utility functions for EngineWarhammer data normalization and processing.
"""

import re
from typing import Any, Optional

from .consts import MAX_SYMPTOMS, MIN_SYMPTOMS


def normalize_disease_name(name: Any) -> Optional[str]:
    """
    Normalize disease name for consistent storage and lookup.

    Args:
        name: Disease name to normalize

    Returns:
        Normalized disease name or None if invalid
    """
    if not name or not isinstance(name, (str, int, float)):
        return None

    # Convert to string and strip whitespace
    normalized = str(name).strip()

    # Remove empty strings
    if not normalized:
        return None

    # Remove BOM and other invisible characters
    normalized = normalized.replace("\ufeff", "").replace("\u200b", "")

    # Normalize whitespace
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized


def normalize_symptom_name(name: Any) -> Optional[str]:
    """
    Normalize symptom name for consistent storage and lookup.

    Args:
        name: Symptom name to normalize

    Returns:
        Normalized symptom name or None if invalid
    """
    if not name or not isinstance(name, (str, int, float)):
        return None

    # Convert to string and strip whitespace
    normalized = str(name).strip()

    # Remove empty strings
    if not normalized:
        return None

    # Remove BOM and other invisible characters
    normalized = normalized.replace("\ufeff", "").replace("\u200b", "")

    # Normalize whitespace
    normalized = re.sub(r"\s+", " ", normalized)

    # Convert to lowercase for consistent matching
    normalized = normalized.lower()

    return normalized


def normalize_probability(value: Any) -> Optional[float]:
    """
    Normalize probability value to float between 0 and 1.

    Args:
        value: Probability value to normalize

    Returns:
        Normalized probability as float or None if invalid
    """
    if value is None:
        return None

    try:
        # Convert to float
        prob = float(value)

        # Ensure it's between 0 and 1
        if 0.0 <= prob <= 1.0:
            return prob
        elif 0.0 <= prob <= 100.0:
            # Convert percentage to decimal
            return prob / 100.0
        else:
            return None

    except (ValueError, TypeError):
        return None


def validate_symptom_list(symptoms: list[str]) -> tuple[bool, str]:
    """
    Validate symptom list for calculation requirements.

    Args:
        symptoms: List of symptom names

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not symptoms:
        return False, "No symptoms provided"

    if len(symptoms) < MIN_SYMPTOMS:
        return False, f"At least {MIN_SYMPTOMS} symptom required"

    if len(symptoms) > MAX_SYMPTOMS:
        return False, f"Maximum {MAX_SYMPTOMS} symptoms allowed"

    # Check for empty or invalid symptoms
    normalized_symptoms = [normalize_symptom_name(s) for s in symptoms]
    if any(s is None for s in normalized_symptoms):
        return False, "Invalid symptom names found"

    # Check for duplicates
    if len(set(normalized_symptoms)) != len(normalized_symptoms):
        return False, "Duplicate symptoms found"

    return True, ""
