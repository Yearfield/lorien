"""
Constants for EngineShortBow symptom matrix processing.
"""

# Expected column names for symptom matrix Excel files
SYMPTOM_COLUMNS = [
    "symptom_name",
    "symptom",
    "name",
    "label",
]

# Default probability range validation
MIN_PROBABILITY = 0.0
MAX_PROBABILITY = 1.0

# Navigation limits
MAX_TOP_LINKED = 5
DEFAULT_TOP_SYMPTOMS = 6
MAX_SELECTED_SYMPTOMS = 5
