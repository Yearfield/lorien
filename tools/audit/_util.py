from __future__ import annotations
import os, sys, re, json, subprocess, importlib, inspect
from typing import Dict, List, Tuple, Set, Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
API_PY_ROOT = os.path.join(REPO_ROOT, "api")
UI_ROOT    = os.path.join(REPO_ROOT, "ui_flutter")

def add_paths() -> None:
    sys.path.insert(0, REPO_ROOT)
    sys.path.insert(0, API_PY_ROOT)

def import_fastapi_app() -> Any:
    add_paths()
    try:
        mod = importlib.import_module("api.app")
        app = getattr(mod, "app", None)
        if app is None:
            raise RuntimeError("api.app.app not found")
        # Touch routes to ensure startup loads them
        _ = getattr(app, "routes", [])
        return app
    except Exception as e:
        print(f"Failed to import FastAPI app: {e}")
        import traceback
        traceback.print_exc()
        raise RuntimeError(f"Failed to import FastAPI app: {e}")

def fix_relative_imports():
    """Fix relative imports when running as standalone scripts"""
    import sys
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

CANON_HEADER = [
    "Vital Measurement","Node 1","Node 2","Node 3","Node 4","Node 5","Diagnostic Triage","Actions"
]

def run(cmd: List[str], cwd: str | None = None, timeout: int = 120) -> Tuple[int,str,str]:
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
        return 124, out, err
    return p.returncode, out, err

ROUTE_EXCLUDES = (
    "/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect"
)
