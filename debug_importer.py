#!/usr/bin/env python3

import sqlite3
import tempfile
import os
from Engines.EngineLongBow.importer import import_rows, ImportOptions, _find_path_cells, _parent_chain
from api.routers.helpers import coerce_rows_to_canonical
import csv
import io

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
csv_data = '''D0,D1,D2,D3,D4,D5,D6,Notes
Root A,child1,,,,,'''

rows = []
reader = csv.DictReader(io.StringIO(csv_data))
for row in reader:
    rows.append(row)

print('Original rows:', rows)
coerced = coerce_rows_to_canonical(rows)
print('Coerced rows:', coerced)

# Test the importer functions
for r in coerced:
    cells = _find_path_cells(r)
    chain = _parent_chain(cells)
    print(f'Row: {r}')
    print(f'Cells: {cells}')
    print(f'Chain: {chain}')

conn.close()
os.unlink(db_path)
print("Debug completed successfully!")
