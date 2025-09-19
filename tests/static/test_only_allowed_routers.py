import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
ROUTERS_DIR = ROOT / "api" / "routers"

ALLOWED = {
    "health.py",
    "import_router.py",
    "tree_export_router.py",
    "tree_basic.py",
    "__init__.py",
}

def test_only_allowed_router_py_files_exist():
    """Ensure only the 4 essential router files exist in api/routers/"""
    py_files = {p.name for p in ROUTERS_DIR.glob("*.py")}
    extra = py_files - ALLOWED
    assert not extra, f"Unexpected router files present: {sorted(extra)}"
