import pytest
from fastapi.testclient import TestClient
from fastapi.routing import APIRoute

REQUIRED = [
  "/import", "/import/preview",
  "/tree/export-json", "/tree/export", "/tree/export.xlsx",
  "/tree/stats", "/tree/progress", "/tree/parents/query",
  "/admin/clear", "/admin/clear-nodes",
  "/tree/conflicts/conflicts", "/tree/parent/{parent_id:int}/children",
  "/tree/next-incomplete-parent-json", "/tree/{parent_id:int}/slot/{slot:int}",
  "/tree/root-options", "/tree/navigate",
  "/dictionary", "/dictionary/export", "/dictionary/export.xlsx",
  "/tree/vm",
]

@pytest.fixture(scope="session")
def app():
    from api.app import app as a
    return a

def _paths(app):
    return set(r.path for r in app.routes if isinstance(r, APIRoute))

def _has(p, paths):
    variants = [p, p.replace("{parent_id:int}","{parent_id}").replace("{slot:int}","{slot}")]
    return any(v in paths or ("/api/v1"+v) in paths for v in variants)

def test_required_endpoints_present(app):
    paths = _paths(app)
    missing = [p for p in REQUIRED if not _has(p, paths)]
    assert not missing, f"Missing endpoints: {missing}"

def test_dual_mounts(app):
    paths = _paths(app)
    base = set()
    for p in paths:
        if p.startswith("/api/v1/"):
            base.add(p[len("/api/v1"):])
        else:
            base.add(p)
    # For each base (except '/'), require both mounts if it exists at least once
    violated = []
    for b in base:
        if b == "/": continue
        has_bare = b in paths
        has_v1 = ("/api/v1"+b) in paths
        if has_bare ^ has_v1:
            violated.append(b)
    assert not violated, f"Dual-mount missing for: {violated}"
