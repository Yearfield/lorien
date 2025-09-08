import importlib, os, re, subprocess, sys, json
from types import ModuleType
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def add_path():
    if ROOT not in sys.path: sys.path.insert(0, ROOT)

def import_app():
    add_path()
    # Try both app entrypoints; return the first that works.
    for mod_name, app_attr in [("api.main","app"), ("api.app","app")]:
        try:
            m = importlib.import_module(mod_name)
            app = getattr(m, app_attr, None)
            if app is not None:
                return app
        except Exception:
            continue
    raise RuntimeError("Could not import FastAPI app from api.main or api.app")

def run(cmd, cwd=ROOT) -> tuple[int,str,str]:
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err

def read_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def list_dart_files():
    ui_root = os.path.join(ROOT, "ui_flutter", "lib")
    for dirpath, _, files in os.walk(ui_root):
        for fn in files:
            if fn.endswith(".dart"):
                yield os.path.join(dirpath, fn)