"""
Static tests to ensure routers use EngineLongBow only.
"""

import pathlib

def test_import_router_uses_longbow_only():
    """Test that import router uses EngineLongBow only."""
    p = pathlib.Path("api/routers/import_router.py")
    src = p.read_text(encoding="utf-8")
    assert "Engines.EngineLongBow" in src
    assert "ingest_file" in src
    assert "apply_import" in src
    assert "import_dataframe" not in src

def test_export_router_uses_longbow_only():
    """Test that export router uses EngineLongBow only."""
    p = pathlib.Path("api/routers/tree_export_router.py")
    src = p.read_text(encoding="utf-8")
    assert "Engines.EngineLongBow" in src
    assert "export_paths_to_csv" in src
    assert "export_paths_to_xlsx" in src
