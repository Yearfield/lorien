import io
import csv
import json
import pytest
from fastapi.testclient import TestClient
from api.main import app

try:
    import openpyxl  # for XLSX path
except Exception:
    openpyxl = None

UPLOAD_CANDIDATES = [
    "/api/v1/workspace/upload",
    "/api/v1/tree/import",
    "/api/v1/workspace/import",
    "/api/v1/import",  # Current working endpoint
]

def _export_header(client: TestClient):
    """Fetch 0-row CSV to get the canonical header row/order"""
    r = client.get("/api/v1/tree/export")
    assert r.status_code == 200, r.text
    text = r.text
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    assert len(rows) >= 1, "export returned no header row"
    return rows[0]  # frozen 8-column header

def _make_rows_for_conflict(header):
    """
    Build duplicate parents with different 5-sets (Alpha => conflict),
    and duplicate parents with identical 5-sets (Beta => NOT a conflict).
    Uses EngineLongBow path-based format: D0->D1->D2->D3->D4->D5->D6
    
    Creates two different parent contexts for the same label to produce conflicts.
    """
    # EngineLongBow expects frozen header: ["D0","D1","D2","D3","D4","D5","D6","Notes"]
    assert header == ["D0","D1","D2","D3","D4","D5","D6","Notes"], f"Expected frozen header, got: {header}"

    def row(d0, d1, d2, d3, d4, d5, d6, notes=""):
        """Create a path row for EngineLongBow"""
        return [d0, d1, d2, d3, d4, d5, d6, notes]

    rows = []
    
    # Alpha => true conflict - create two different parent contexts with same label at depth 1
    # Context 1: Root1 -> Alpha -> {A,B,C,D,E} (5 direct children)
    rows.append(row("Root1", "Alpha", "A", "", "", "", ""))
    rows.append(row("Root1", "Alpha", "B", "", "", "", ""))
    rows.append(row("Root1", "Alpha", "C", "", "", "", ""))
    rows.append(row("Root1", "Alpha", "D", "", "", "", ""))
    rows.append(row("Root1", "Alpha", "E", "", "", "", ""))
    
    # Context 2: Root2 -> Alpha -> {A,B,C,D,X} (5 direct children, differs by X vs E)
    rows.append(row("Root2", "Alpha", "A", "", "", "", ""))
    rows.append(row("Root2", "Alpha", "B", "", "", "", ""))
    rows.append(row("Root2", "Alpha", "C", "", "", "", ""))
    rows.append(row("Root2", "Alpha", "D", "", "", "", ""))
    rows.append(row("Root2", "Alpha", "X", "", "", "", ""))
    
    # Beta => identical 5-sets (no conflict)
    # Context 1: Root1 -> Beta -> {K,L,M,N,O} (5 direct children)
    rows.append(row("Root1", "Beta", "K", "", "", "", ""))
    rows.append(row("Root1", "Beta", "L", "", "", "", ""))
    rows.append(row("Root1", "Beta", "M", "", "", "", ""))
    rows.append(row("Root1", "Beta", "N", "", "", "", ""))
    rows.append(row("Root1", "Beta", "O", "", "", "", ""))
    
    # Context 2: Root2 -> Beta -> {K,L,M,N,O} (identical 5-set)
    rows.append(row("Root2", "Beta", "K", "", "", "", ""))
    rows.append(row("Root2", "Beta", "L", "", "", "", ""))
    rows.append(row("Root2", "Beta", "M", "", "", "", ""))
    rows.append(row("Root2", "Beta", "N", "", "", "", ""))
    rows.append(row("Root2", "Beta", "O", "", "", "", ""))
    
    return rows

def _build_csv_bytes(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    return buf.getvalue().encode("utf-8")

def _try_upload(client: TestClient, file_bytes: bytes, filename: str):
    for path in UPLOAD_CANDIDATES:
        r = client.post(path + "?mode=replace", files={"file": (filename, file_bytes, "text/csv")})
        if r.status_code in (200, 201, 202, 204):
            return r
        if r.status_code in (404, 405):
            continue
        # allow header 422 to bubble for better diagnostics
        return r
    pytest.skip("No known upload endpoint is available")

# Use the client fixture from conftest.py that sets up the test database

def test_import_then_conflicts_with_autodiscovered_header(client):
    """Test that we can discover the header format and create conflicts correctly"""
    # Debug: Check what database path is being used
    import os
    print(f"DEBUG: LORIEN_DB_PATH = {os.environ.get('LORIEN_DB_PATH', 'NOT SET')}")
    
    header = _export_header(client)
    rows = _make_rows_for_conflict(header)
    csv_bytes = _build_csv_bytes(header, rows)
    r = _try_upload(client, csv_bytes, "conflicts.csv")
    assert r.status_code in (200, 201, 202, 204), f"Upload failed: {r.status_code} {r.text}"
    
    # Debug: Check what was actually imported
    print(f"DEBUG: Import response: {r.json()}")
    
    # Debug: Check what nodes exist in the database
    import sqlite3
    import os
    db_path = os.environ["LORIEN_DB_PATH"]
    conn = sqlite3.connect(db_path)
    try:
        nodes = conn.execute("SELECT id, parent_id, label, depth, slot FROM nodes ORDER BY depth, label").fetchall()
        print(f"DEBUG: Database nodes: {nodes}")
    finally:
        conn.close()

    # Verify conflicts list catches Alpha, excludes Beta
    q = "/api/v1/tree/conflicts/conflicts?limit=50&only_exact_five=true&only_duplicate_parents=true&require_variant_sets=true"
    resp = client.get(q)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    items = data.get("items", [])
    labels = [(it.get("label"), it.get("variant_sets", 0)) for it in items]
    
    # Debug: Print what we got
    print(f"DEBUG: Conflicts response: {data}")
    print(f"DEBUG: Items: {items}")
    print(f"DEBUG: Labels: {labels}")
    
    assert any(lbl == "Alpha" and (vs or 0) >= 2 for lbl, vs in labels), f"Alpha missing: {labels}"
    assert not any(lbl == "Beta" for lbl, _ in labels), f"Beta should NOT be flagged: {labels}"
