import io
import json
import pytest
from fastapi.testclient import TestClient
from api.main import app

try:
    import openpyxl  # type: ignore
except Exception:
    openpyxl = None

UPLOAD_CANDIDATES = [
    "/api/v1/import",               # Current working endpoint
    "/api/v1/workspace/upload",     # preferred
    "/api/v1/tree/import",          # legacy
    "/api/v1/workspace/import",     # alt
]

@pytest.fixture
def client():
    return TestClient(app)

def _make_conflict_workbook() -> bytes:
    """
    Build a minimal XLSX with two parents sharing same (label,depth) but different 5-child sets:
      Parent label: "Alpha", depth=1
        P1 children: A,B,C,D,E
        P2 children: A,B,C,D,X   # differs by one label
    Also add a negative control:
      Parent label: "Beta", depth=1
        two parents with identical 5-set -> must NOT be flagged
    NOTE: Column order uses a safe fallback header. If your importer requires the frozen
    8-col header, swap to that exact header here.
    """
    assert openpyxl is not None, "openpyxl not installed for XLSX creation"
    wb = openpyxl.Workbook()
    ws = wb.active
    # Safe fallback header used by many tree importers:
    header = ["parent_label","depth","s1","s2","s3","s4","s5","notes"]
    ws.append(header)

    def row(plabel, depth, s1,s2,s3,s4,s5, notes=""):
        ws.append([plabel, depth, s1,s2,s3,s4,s5, notes])

    # Alpha duplicates with variant sets (should be flagged)
    row("Alpha", 1, "A","B","C","D","E")
    row("Alpha", 1, "A","B","C","D","X")

    # Beta duplicates with identical set (should NOT be flagged)
    row("Beta", 1, "K","L","M","N","O")
    row("Beta", 1, "K","L","M","N","O")

    buff = io.BytesIO()
    wb.save(buff)
    return buff.getvalue()

def _post_upload(client: TestClient, file_bytes: bytes):
    """
    Try known upload endpoints. If none exist, skip the test.
    Assumes multipart form: field name 'file'.
    """
    for path in UPLOAD_CANDIDATES:
        r = client.post(path, files={"file": ("conflicts.xlsx", file_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
        if r.status_code in (200, 201, 202, 204):
            return r
        if r.status_code == 415:  # wrong media / expects CSV
            r2 = client.post(path, files={"file": ("conflicts.csv", file_bytes, "text/csv")})
            if r2.status_code in (200, 201, 202, 204):
                return r2
        if r.status_code in (404,405):
            continue
        # Any other code is meaningful, return it for diagnostics
        return r
    pytest.skip("No known upload endpoint is available")

@pytest.fixture
def client():
    # If your app uses a file DB path, consider isolating per-test DB via env var or settings override.
    return TestClient(app)

def test_import_then_conflicts_lists_variant_sets(client):
    # 1) Upload the synthetic workbook
    if openpyxl is None:
        pytest.skip("openpyxl not installed")
    payload = _make_conflict_workbook()
    r = _post_upload(client, payload)
    assert r.status_code in (200,201,202,204), f"Upload failed: {r.status_code} {r.text}"

    # 2) Query the conflicts list (canonical flags on)
    q = "/api/v1/tree/conflicts/conflicts?limit=50&only_exact_five=true&only_duplicate_parents=true&require_variant_sets=true"
    resp = client.get(q)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    items = data.get("items", [])
    # 3) Assert "Alpha" appears (variant sets >= 2), "Beta" does not
    labels = [(it.get("label"), it.get("variant_sets", 0)) for it in items]
    assert any(lbl == "Alpha" and (vs or 0) >= 2 for lbl,vs in labels), f"Alpha wasn't detected as conflict: {labels}"
    assert not any(lbl == "Beta" for lbl, _ in labels), f"Beta (identical sets) should not be flagged: {labels}"
