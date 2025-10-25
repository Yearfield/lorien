"""
Core calculation logic for EngineShortBow symptom navigation.
"""

import logging
from dataclasses import dataclass
from typing import Optional

from .utils import format_probability

logger = logging.getLogger(__name__)


@dataclass
class SymptomLink:
    """Represents a link between two symptoms with probability."""

    from_symptom: str
    to_symptom: str
    probability: float

    def __str__(self) -> str:
        return f"{self.from_symptom} -> {self.to_symptom} ({format_probability(self.probability)})"


@dataclass
class ShortBowCalculationResult:
    """Result of a ShortBow navigation calculation."""

    current_symptom: str
    top_linked: list[SymptomLink]
    excluded_symptoms: list[str]
    total_available: int

    def __str__(self) -> str:
        return f"Top {len(self.top_linked)} linked to '{self.current_symptom}' (excluded: {len(self.excluded_symptoms)})"


def get_top_linked_symptoms(
    current_symptom: str,
    symptom_links: dict,
    exclude: Optional[list[str]] = None,
    max_results: int = 5,
) -> ShortBowCalculationResult:
    """
    Get top linked symptoms for a given current symptom.

    Args:
        current_symptom: The current symptom to find links for
        symptom_links: Dict mapping (from_symptom, to_symptom) -> probability
        exclude: List of symptoms to exclude from results
        max_results: Maximum number of results to return

    Returns:
        ShortBowCalculationResult with top linked symptoms
    """
    if exclude is None:
        exclude = []

    # Normalize current symptom and exclusions
    current_normalized = current_symptom.lower().strip()
    exclude_normalized = [s.lower().strip() for s in exclude]

    # Find all links from current symptom
    current_links = []
    for (from_symptom, to_symptom), probability in symptom_links.items():
        if from_symptom == current_normalized:
            # Skip if in exclusion list
            if to_symptom in exclude_normalized:
                continue
            # Skip self-links
            if to_symptom == current_normalized:
                continue

            current_links.append(
                SymptomLink(
                    from_symptom=from_symptom, to_symptom=to_symptom, probability=probability
                )
            )

    # Sort by probability descending
    current_links.sort(key=lambda x: x.probability, reverse=True)

    # Take top results
    top_linked = current_links[:max_results]

    logger.info(
        f"Found {len(current_links)} total links for '{current_symptom}', returning top {len(top_linked)}"
    )

    return ShortBowCalculationResult(
        current_symptom=current_symptom,
        top_linked=top_linked,
        excluded_symptoms=exclude,
        total_available=len(current_links),
    )


def get_top_symptoms_by_average_linkage(
    symptom_links: dict, all_symptoms: list[str], max_results: int = 6
) -> list[tuple[str, float]]:
    """
    Get symptoms with highest average linkage to all other symptoms.

    Args:
        symptom_links: Dict mapping (from_symptom, to_symptom) -> probability
        all_symptoms: List of all available symptoms
        max_results: Maximum number of results to return

    Returns:
        List of (symptom, average_probability) tuples sorted by average descending
    """
    symptom_averages = {}

    for symptom in all_symptoms:
        symptom_normalized = symptom.lower().strip()

        # Find all outgoing links from this symptom
        outgoing_links = []
        for (from_symptom, to_symptom), probability in symptom_links.items():
            if from_symptom == symptom_normalized:
                outgoing_links.append(probability)

        # Calculate average probability
        if outgoing_links:
            average_prob = sum(outgoing_links) / len(outgoing_links)
            symptom_averages[symptom] = average_prob
        else:
            symptom_averages[symptom] = 0.0

    # Sort by average probability descending
    sorted_symptoms = sorted(symptom_averages.items(), key=lambda x: x[1], reverse=True)

    return sorted_symptoms[:max_results]
