"""
Canonical constants for the decision tree application.
"""

# Application versioning
APP_VERSION = "1.0.0"
APP_NAME = "Decision Tree Manager"
APP_DESCRIPTION = "Cross-platform decision tree management with offline-first storage"

# Canonical column headers (exact order + names)
CANON_HEADERS = [
    "Vital Measurement",  # depth=0, slot=0 root label
    "Node 1",            # depth=1, slot=1
    "Node 2",            # depth=2, slot=2
    "Node 3",            # depth=3, slot=3
    "Node 4",            # depth=4, slot=4
    "Node 5",            # depth=5, slot=5 (leaf)
    "Diagnostic Triage", # attached to leaf node
    "Actions"            # attached to leaf node
]

# Node depth constants
ROOT_DEPTH = 0
MAX_DEPTH = 5
LEAF_DEPTH = 5

# Slot constants
ROOT_SLOT = 0
MIN_CHILD_SLOT = 1
MAX_CHILD_SLOT = 5

# Import/Export strategies
STRATEGY_PLACEHOLDER = "placeholder"
STRATEGY_PRUNE = "prune"
STRATEGY_PROMPT = "prompt"

# Placeholder text for missing nodes
PLACEHOLDER_TEXT = "[MISSING]"

# File extensions
EXCEL_EXTENSIONS = ['.xlsx', '.xls']
CSV_EXTENSIONS = ['.csv']

# CLI exit codes
EXIT_SUCCESS = 0
EXIT_VALIDATION_ERROR = 1
EXIT_IMPORT_ERROR = 2
EXIT_EXPORT_ERROR = 3
EXIT_SYSTEM_ERROR = 4
