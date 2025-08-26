import ast
import pathlib

FORBIDDEN = {
    "sqlite3",
    "sqlalchemy",
    "gspread",
    "core.storage",
    "storage.sqlite",
    "importers",
    "exporters",
}

def test_ui_streamlit_has_no_forbidden_imports():
    root = pathlib.Path(__file__).resolve().parents[2]
    ui_dir = root / "ui_streamlit"
    offenders = []
    for py in ui_dir.rglob("*.py"):
        src = py.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(py))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for n in node.names:
                    name = n.name
                    if any(name == f or name.startswith(f + ".") for f in FORBIDDEN):
                        offenders.append((str(py), name))
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if any(mod == f or mod.startswith(f + ".") for f in FORBIDDEN):
                    offenders.append((str(py), mod))
    assert not offenders, f"Forbidden imports in ui_streamlit:\n" + "\n".join(f"{p} -> {m}" for p, m in offenders)
