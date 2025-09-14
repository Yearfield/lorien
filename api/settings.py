import os

# Default DB path used when env is not set
DEFAULT_DB = os.path.expanduser("~/.local/share/lorien/app.db")

def get_db_path() -> str:
    """Return the SQLite DB path, reading env at call time.

    Tests and runtime can override using LORIEN_DB_PATH without import-time capture.
    """
    return os.environ.get("LORIEN_DB_PATH", DEFAULT_DB)

# Backward-compat alias (avoid using; prefer get_db_path())
# Note: This is evaluated at import time, which may not work for tests
# Use get_db_path() instead for runtime evaluation
