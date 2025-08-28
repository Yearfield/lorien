"""
Constants for the Lorien decision tree application.
"""

from core.version import __version__ as APP_VERSION

# API Configuration
API_PREFIX = "/api/v1"
DEFAULT_PAGE_SIZE = 100
MAX_PAGE_SIZE = 1000

# Database Configuration
DEFAULT_DB_PATH = "sqlite.db"
WAL_MODE = True
FOREIGN_KEYS = True

# Feature Flags
LLM_ENABLED_DEFAULT = False

# CSV Export Contract (Frozen)
CSV_HEADERS = [
    "Vital Measurement",
    "Node 1", 
    "Node 2",
    "Node 3",
    "Node 4",
    "Node 5",
    "Diagnostic Triage",
    "Actions"
]

# Tree Constraints
MAX_CHILDREN_PER_PARENT = 5
MAX_TREE_DEPTH = 5
