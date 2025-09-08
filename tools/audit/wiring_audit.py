from __future__ import annotations
from typing import List, Dict, Any, Tuple, Set
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import import_fastapi_app, ROUTE_EXCLUDES

def collect_routes() -> List[Dict[str,Any]]:
    app = import_fastapi_app()
    out = []
    for r in app.routes:
        path = getattr(r, "path", None) or getattr(r, "path_format", None)
        if not path or any(path.startswith(ex) for ex in ROUTE_EXCLUDES):
            continue
        methods = sorted(list(getattr(r, "methods", set()) or []))
        name = getattr(r, "name", "")
        out.append({"path": path, "methods": methods, "name": name})
    out.sort(key=lambda x: (x["path"], ",".join(x["methods"])))
    return out

def map_dual_mount(routes: List[Dict[str,Any]]) -> Dict[str,Dict[str,Any]]:
    # base path (no /api/v1) → has_bare, has_v1
    idx = {}
    # Accept both bare and /api/v1 prefixed
    for r in routes:
        p = r["path"]
        if p.startswith("/api/v1/"):
            base = p[len("/api/v1"):]  # keep leading /
            rec = idx.setdefault(base, {"bare": False, "v1": False, "examples": []})
            rec["v1"] = True; rec["examples"].append(p)
        else:
            base = p
            rec = idx.setdefault(base, {"bare": False, "v1": False, "examples": []})
            rec["bare"] = True; rec["examples"].append(p)
    return idx

if __name__ == "__main__":
    routes = collect_routes()
    pairs  = map_dual_mount(routes)
    print({"routes": routes, "dual_pairs": pairs})
