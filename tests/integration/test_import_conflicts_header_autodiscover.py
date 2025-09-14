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
    r = client.get("/api/v1/tree/export?format=csv&limit=0")
    assert r.status_code == 200, r.text
    text = r.text
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    assert len(rows) >= 1, "export returned no header row"
    return rows[0]  # frozen 8-column header

def _make_rows_for_conflict(header):
    """
    Build two duplicate parents with different 5-sets (Alpha => conflict),
    and two duplicate parents with identical 5-sets (Beta => NOT a conflict).
    We fill only the columns we know; unknown columns remain empty.
    Header order is preserved exactly from export.
    """
    # Try to infer column names used for parent label/depth/slots 1..5.
    # We support common names but honor exact match if present.
    def col(name, fallbacks):
        for n in [name] + fallbacks:
            if n in header: 
                return n
        raise AssertionError(f"Required column missing: {name} / {fallbacks}")

    c_label = col("Vital Measurement", ["parent_label", "Parent Label", "label", "Label"])
    c_nodes = [col(f"Node {i}", [f"s{i}", f"S{i}", f"slot{i}", f"Slot {i}"]) for i in range(1, 6)]
    c_triage = col("Diagnostic Triage", ["triage", "Triage", "diagnostic_triage"])
    c_actions = col("Actions", ["actions", "Actions"])

    def row(plabel, slots, triage="", actions=""):
        d = {h: "" for h in header}
        d[c_label] = plabel
        for i, val in enumerate(slots, start=1):
            if i <= 5:  # Only fill up to Node 5
                d[c_nodes[i-1]] = val
        d[c_triage] = triage
        d[c_actions] = actions
        return [d[h] for h in header]

    rows = []
    # Create a root node first, then create parent nodes under it
    # This matches the structure expected by the conflicts detection logic
    rows.append(row("Root", []))  # Root node
    # Alpha => true conflict - create two different parent nodes with same label but different children
    rows.append(row("Alpha", ["A", "B", "C", "D", "E"]))
    rows.append(row("Alpha", ["A", "B", "C", "D", "X"]))
    # Beta => identical 5-set (no conflict)
    rows.append(row("Beta", ["K", "L", "M", "N", "O"]))
    rows.append(row("Beta", ["K", "L", "M", "N", "O"]))
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
