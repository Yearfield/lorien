import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tools.audit._util import import_app
from fastapi.routing import APIRoute
from collections import defaultdict

def collect_routes():
    app = import_app()
    routes = []
    for r in app.routes:
        if isinstance(r, APIRoute):
            routes.append({
                "path": r.path,
                "name": r.name,
                "methods": sorted(list(r.methods or [])),
            })
    return routes

def dual_mount_map(routes):
    # map base path without /api/v1 prefix to whether bare & v1 exist
    base = defaultdict(lambda: {"bare": False, "v1": False, "examples": []})
    for r in routes:
        p = r["path"]
        if p.startswith("/api/v1/"):
            b = p[len("/api/v1"):]
            base[b]["v1"] = True
            base[b]["examples"].append(p)
        else:
            base[p]["bare"] = True
            base[p]["examples"].append(p)
    return base
