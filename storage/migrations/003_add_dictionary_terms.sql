-- Migration: Add dictionary_terms table and indexes
CREATE TABLE IF NOT EXISTS dictionary_terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL CHECK (type IN ('vital_measurement','node_label','outcome_template')),
    term TEXT NOT NULL,
    normalized TEXT NOT NULL,
    hints TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Uniqueness by (type, normalized) to avoid case/space dupes
CREATE UNIQUE INDEX IF NOT EXISTS ux_dictionary_type_normalized
    ON dictionary_terms(type, normalized);

-- Search helpers
CREATE INDEX IF NOT EXISTS idx_dictionary_type_term
    ON dictionary_terms(type, term);

-- Touch updated_at on update
CREATE TRIGGER IF NOT EXISTS trg_dictionary_terms_upd
AFTER UPDATE ON dictionary_terms
FOR EACH ROW
BEGIN
  UPDATE dictionary_terms SET updated_at=CURRENT_TIMESTAMP WHERE id=OLD.id;
END;
