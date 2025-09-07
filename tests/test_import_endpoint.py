import io
import pandas as pd
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

CANON_HEADERS = [
    "Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5",
    "Diagnostic Triage", "Actions"
]

def test_import_success_xlsx():
    df = pd.DataFrame(columns=CANON_HEADERS, data=[])
    buf = io.BytesIO()
    # Important: use openpyxl engine for xlsx
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False)
    buf.seek(0)
    r = client.post("/api/v1/import", files={"file": ("ok.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_import_success_csv():
    df = pd.DataFrame(columns=CANON_HEADERS, data=[])
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    r = client.post("/api/v1/import", files={"file": ("ok.csv", buf, "text/csv")})
    assert r.status_code == 200
    assert r.json()["ok"] is True

def test_import_bad_header_csv():
    df = pd.DataFrame(columns=["Wrong1","Wrong2"], data=[])
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    r = client.post("/api/v1/import", files={"file": ("bad.csv", buf, "text/csv")})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert detail["loc"] == ["header"]
    assert detail["msg"] == "Header mismatch"
    ctx = detail["ctx"]
    assert ctx["row"] == 1
    assert "expected" in ctx and "received" in ctx
    assert isinstance(ctx["expected"], list) and isinstance(ctx["received"], list)

def test_import_wrong_case_header():
    df = pd.DataFrame(columns=["vital measurement", "node 1", "node 2", "node 3", "node 4", "node 5", "diagnostic triage", "actions"], data=[])
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    r = client.post("/api/v1/import", files={"file": ("wrong_case.csv", buf, "text/csv")})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert detail["loc"] == ["header"]
    assert detail["msg"] == "Header mismatch"
    ctx = detail["ctx"]
    assert ctx["row"] == 1
    assert ctx["col_index"] == 0  # First column mismatch
    assert ctx["expected"] == CANON_HEADERS
    assert ctx["received"] == ["vital measurement", "node 1", "node 2", "node 3", "node 4", "node 5", "diagnostic triage", "actions"]

def test_import_missing_column():
    df = pd.DataFrame(columns=["Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5", "Diagnostic Triage"], data=[])
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    r = client.post("/api/v1/import", files={"file": ("missing_col.csv", buf, "text/csv")})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert detail["loc"] == ["header"]
    assert detail["msg"] == "Header mismatch"
    ctx = detail["ctx"]
    assert ctx["row"] == 1
    assert ctx["col_index"] == 7  # Missing column at index 7
    assert ctx["expected"] == CANON_HEADERS
    assert ctx["received"] == ["Vital Measurement", "Node 1", "Node 2", "Node 3", "Node 4", "Node 5", "Diagnostic Triage"]

def test_import_extra_column():
    df = pd.DataFrame(columns=CANON_HEADERS + ["Extra"], data=[])
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    r = client.post("/api/v1/import", files={"file": ("extra_col.csv", buf, "text/csv")})
    assert r.status_code == 422
    detail = r.json()["detail"][0]
    assert detail["loc"] == ["header"]
    assert detail["msg"] == "Header mismatch"
    ctx = detail["ctx"]
    assert ctx["row"] == 1
    assert ctx["col_index"] == 8  # Extra column at index 8
    assert ctx["expected"] == CANON_HEADERS
    assert ctx["received"] == CANON_HEADERS + ["Extra"]

def test_import_dual_mount():
    """Test import works on both root and /api/v1 mounts."""
    df = pd.DataFrame(columns=CANON_HEADERS, data=[])
    buf = io.BytesIO()
    df.to_csv(buf, index=False)
    buf.seek(0)
    files = {"file": ("ok.csv", buf, "text/csv")}

    # Test root mount
    r1 = client.post("/import", files=files)
    assert r1.status_code == 200

    # Test api/v1 mount
    buf.seek(0)  # Reset buffer
    r2 = client.post("/api/v1/import", files=files)
    assert r2.status_code == 200
