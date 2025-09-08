from tools.audit.wiring_audit import collect_routes
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Required core endpoints (base form; test also relies on dual-mount test)
REQUIRED = {
    "/": {"GET"},  # Root endpoint now dual-mounted
    "/import": {"POST"},
    "/tree/export-json": {"GET"},
    "/tree/stats": {"GET"},
    "/tree/missing-slots-json": {"GET"},
    "/admin/clear": {"POST"},
    "/admin/clear-nodes": {"POST"},
    "/tree/next-incomplete-parent-json": {"GET"},
    "/tree/{parent_id}/slot/{slot}": {"PUT"},
    "/tree/conflicts": {"GET"},
    "/tree/conflicts/group": {"GET"},
    "/tree/conflicts/group/resolve": {"POST"},
    "/tree/labels": {"GET"},
    "/tree/labels/{label}/aggregate": {"GET"},
    "/tree/labels/{label}/apply-default": {"POST"},
    "/tree/vm": {"POST"},
    "/tree/suggest/labels": {"GET"},
    "/tree/children": {"GET"},
    "/tree/root-options": {"GET"},
    "/tree/navigate": {"GET"},
}

def norm(p):  # normalize templated path segments
    return p.replace("{parent_id}", "{parent_id}").replace("{slot}", "{slot}").replace("{label}", "{label}")

def test_required_core_endpoints_discovered():
    routes = collect_routes()
    seen = {}
    for r in routes:
        seen.setdefault(r["path"], set()).update(r["methods"])
    missing = []
    for path, methods in REQUIRED.items():
        ok = False
        for sp, sm in seen.items():
            if norm(sp) == norm(path) and methods.issubset(sm):
                ok = True; break
        if not ok:
            missing.append(f"{path} {methods}")
    assert not missing, "Missing or method-mismatched endpoints:\n" + "\n".join(missing)
