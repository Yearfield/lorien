"""
Integration test for import/export with >5 children per parent.
"""

import io
import csv
import json
from api.main import app
from fastapi.testclient import TestClient
from api.db.migrate import apply_migrations
import os
import pytest

FROZEN = ["D0","D1","D2","D3","D4","D5","D6","Notes"]


def make_csv(rows):
    """Create CSV content with frozen header."""
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(FROZEN)
    for r in rows:
        w.writerow(r)
    buf.seek(0)
    return buf


def test_import_many_children_roundtrip(tmp_path, monkeypatch):
    """Test that EngineLongBow can import and export parents with >5 children."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    client = TestClient(app)

    # Build a parent with 7 direct children at D2 (two D0 contexts -> two parents, but we care about storage >5)
    rows = []
    # RootX -> ParentA -> children G1..G7
    for child in ["G1","G2","G3","G4","G5","G6","G7"]:
        rows.append(["RootX","ParentA", child, "", "", "", "", ""])

    # Upload (replace)
    buf = make_csv(rows)
    files = {"file": ("many_children.csv", buf.read(), "text/csv")}
    r = client.post("/api/v1/import?mode=replace", files=files)
    assert r.status_code in (200,201), f"Upload failed: {r.status_code} {r.text}"

    # Export CSV
    r = client.get("/api/v1/tree/export?format=csv&limit=100")
    assert r.status_code == 200

    # Parse exported CSV and verify we got all 7 children
    exported_text = r.text
    reader = csv.reader(io.StringIO(exported_text))
    exported_rows = list(reader)
    
    # Should have header + at least 7 data rows (may include root/parent nodes)
    assert len(exported_rows) >= 8  # header + at least 7 data rows
    
    # Check that all 7 children are present (labels are lowercase in export)
    parent_a_rows = [row for row in exported_rows[1:] if len(row) >= 3 and row[1] == "parenta"]
    assert len(parent_a_rows) >= 7, f"Expected at least 7 parenta rows, got {len(parent_a_rows)}"
    
    # Check that all G1-G7 children are present (labels are lowercase in export)
    children = [row[2] for row in parent_a_rows if row[2].startswith("g")]
    expected_children = ["g1","g2","g3","g4","g5","g6","g7"]
    assert set(children) == set(expected_children), f"Expected {expected_children}, got {children}"

    # Count how many rows include 'rootx,parenta,g' - should be >=7 for the first test (labels are lowercase in export)
    csv_text = client.get("/api/v1/tree/export?format=csv&limit=200").text
    assert csv_text.count("rootx,parenta,g") >= 7, f"Expected >=7 children persisted and exported via LongBow. Exported rows:\n{csv_text}"


def test_import_multiple_parents_with_many_children(tmp_path, monkeypatch):
    """Test multiple parents each with >5 children."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    client = TestClient(app)

    # Create two different parents, each with 6 children
    rows = []
    
    # Root1 -> ParentA -> children A1..A6
    for child in ["A1","A2","A3","A4","A5","A6"]:
        rows.append(["Root1","ParentA", child, "", "", "", "", ""])
    
    # Root2 -> ParentB -> children B1..B6  
    for child in ["B1","B2","B3","B4","B5","B6"]:
        rows.append(["Root2","ParentB", child, "", "", "", "", ""])

    # Upload (replace)
    buf = make_csv(rows)
    files = {"file": ("multiple_many_children.csv", buf.read(), "text/csv")}
    r = client.post("/api/v1/import?mode=replace", files=files)
    assert r.status_code in (200,201), f"Upload failed: {r.status_code} {r.text}"

    # Export CSV and verify both parents have 6 children
    r = client.get("/api/v1/tree/export?format=csv&limit=100")
    assert r.status_code == 200

    exported_text = r.text
    reader = csv.reader(io.StringIO(exported_text))
    exported_rows = list(reader)
    
    # Should have header + 12 data rows (6 + 6)
    assert len(exported_rows) == 13  # header + 12 data rows
    
    # Check ParentA has 6 children
    parent_a_rows = [row for row in exported_rows[1:] if len(row) >= 3 and row[1] == "ParentA"]
    assert len(parent_a_rows) == 6, f"Expected 6 ParentA rows, got {len(parent_a_rows)}"
    
    # Check ParentB has 6 children
    parent_b_rows = [row for row in exported_rows[1:] if len(row) >= 3 and row[1] == "ParentB"]
    assert len(parent_b_rows) == 6, f"Expected 6 ParentB rows, got {len(parent_b_rows)}"
    
    # Count how many rows include 'RootX,ParentA,G' - should be >=7 for the first test
    csv_text = client.get("/api/v1/tree/export?format=csv&limit=200").text
    assert csv_text.count("RootX,ParentA,G") >= 7, f"Expected >=7 children persisted and exported via LongBow. Exported rows:\n{csv_text}"


def test_conflicts_still_work_with_exactly_five_children(tmp_path, monkeypatch):
    """Test that conflicts detection still works for parents with exactly 5 children."""
    db = tmp_path / "app.db"
    monkeypatch.setenv("LORIEN_DB_PATH", str(db))
    apply_migrations(str(db))

    client = TestClient(app)

    # Create two different contexts for the same parent label, each with exactly 5 children
    # This should create a conflict
    rows = []
    
    # Root1 -> Alpha -> {A,B,C,D,E} (5 children)
    for child in ["A","B","C","D","E"]:
        rows.append(["Root1","Alpha", child, "", "", "", "", ""])
    
    # Root2 -> Alpha -> {A,B,C,D,X} (5 children, differs by X vs E)
    for child in ["A","B","C","D","X"]:
        rows.append(["Root2","Alpha", child, "", "", "", "", ""])

    # Upload (replace)
    buf = make_csv(rows)
    files = {"file": ("conflicts_test.csv", buf.read(), "text/csv")}
    r = client.post("/api/v1/import?mode=replace", files=files)
    assert r.status_code in (200,201), f"Upload failed: {r.status_code} {r.text}"

    # Check conflicts - should detect Alpha as having variant 5-child sets
    r = client.get("/api/v1/tree/conflicts/conflicts?limit=50&only_exact_five=true&only_duplicate_parents=true&require_variant_sets=true")
    assert r.status_code == 200
    
    data = r.json()
    items = data.get("items", [])
    
    # Should find Alpha as a conflict
    alpha_conflicts = [item for item in items if item.get("label") == "Alpha"]
    assert len(alpha_conflicts) > 0, f"Expected Alpha conflict, got: {[item.get('label') for item in items]}"
    
    # Verify the conflict has exactly 5 children and variant sets
    alpha_conflict = alpha_conflicts[0]
    assert alpha_conflict.get("child_count") == 5
    assert alpha_conflict.get("variant_sets") >= 2
    assert alpha_conflict.get("duplicate_parents") >= 2
