"""
Constants for EngineLongBow path-based ingest system.
"""

# Frozen 8-column export header (order & names must match exactly)
FROZEN_HEADER = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "Notes"]

# Path columns (D0..D6) - the first 7 columns are the path
PATH_COLUMNS = FROZEN_HEADER[:7]  # ["D0", "D1", "D2", "D3", "D4", "D5", "D6"]

# Notes column (ignored for ingestion)
NOTES_COLUMN = FROZEN_HEADER[7]  # "Notes"
