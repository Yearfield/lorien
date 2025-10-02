#!/usr/bin/env python3

import sqlite3
import tempfile
import os
from Engines.EngineLongBow.import_analyzer import analyze_max_children

# Create a test database
with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
    db_path = f.name

# Initialize database
conn = sqlite3.connect(db_path)
conn.execute("""
CREATE TABLE nodes (
    id INTEGER PRIMARY KEY,
    parent_id INTEGER REFERENCES nodes(id),
    depth INTEGER NOT NULL,
    slot INTEGER NULL,
    label TEXT NOT NULL
)
""")
conn.commit()

# Test data
rows = [
    {"D0": "Root A", "D1": "cough", "D2": "", "D3": "", "D4": "", "D5": "", "D6": "", "Notes": ""},
    {"D0": "Root A", "D1": "cough", "D2": "dry", "D3": "", "D4": "", "D5": "", "D6": "", "Notes": ""},
    {"D0": "Root A", "D1": "cough", "D2": "wet", "D3": "", "D4": "", "D5": "", "D6": "", "Notes": ""},
    {"D0": "Root A", "D1": "cough", "D2": "fever", "D3": "", "D4": "", "D5": "", "D6": "", "Notes": ""},
    {"D0": "Root A", "D1": "cough", "D2": "hemoptysis", "D3": "", "D4": "", "D5": "", "D6": "", "Notes": ""},
    {"D0": "Root A", "D1": "cough", "D2": "shortness", "D3": "", "D4": "", "D5": "", "D6": "", "Notes": ""},
    {"D0": "Root A", "D1": "cough", "D2": "wheeze", "D3": "", "D4": "", "D5": "", "D6": "", "Notes": ""},
    {"D0": "Root A", "D1": "cough", "D2": "stridor", "D3": "", "D4": "", "D5": "", "D6": "", "Notes": ""},
]

print("Testing analyze_max_children...")
violations = analyze_max_children(conn, rows, mode="replace")
print(f"Violations: {violations}")

conn.close()
os.unlink(db_path)
print("Test completed successfully!")
