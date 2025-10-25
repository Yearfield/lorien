"""
Utility functions for EngineShortBow.
"""

import re


def normalize_symptom_name(symptom: str) -> str:
    """
    Normalize symptom name for consistent matching.

    Args:
        symptom: Raw symptom name

    Returns:
        Normalized symptom name (lowercase, trimmed, spaces normalized)
    """
    if not symptom or not isinstance(symptom, str):
        return ""

    # Convert to lowercase and strip whitespace
    normalized = symptom.lower().strip()

    # Replace multiple spaces with single space
    normalized = re.sub(r"\s+", " ", normalized)

    # Remove special characters except alphanumeric, spaces, hyphens, underscores
    normalized = re.sub(r"[^\w\s\-]", "", normalized)

    return normalized


def validate_probability(probability: float) -> bool:
    """
    Validate that probability is within valid range.

    Args:
        probability: Probability value to validate

    Returns:
        True if valid (0.0 <= probability <= 1.0), False otherwise
    """
    return isinstance(probability, (int, float)) and 0.0 <= probability <= 1.0


def format_probability(probability: float, decimals: int = 3) -> str:
    """
    Format probability for display.

    Args:
        probability: Probability value
        decimals: Number of decimal places

    Returns:
        Formatted probability string
    """
    return f"{probability:.{decimals}f}"
