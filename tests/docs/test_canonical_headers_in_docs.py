from pathlib import Path

CANON = "Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions"

def test_canonical_headers_present():
    root = Path(__file__).resolve().parents[2] / "docs"
    hits = 0
    for p in root.rglob("*.md"):
        if CANON in p.read_text(encoding="utf-8"):
            hits += 1
    assert hits >= 1, "Canonical headers not documented anywhere"
