-- Migration: Add medical dictionary table for term management
-- Date: 2025-01-27
-- Purpose: Add dictionary functionality for medical terms with definitions, synonyms, and tree relationships

-- Medical dictionary table
CREATE TABLE IF NOT EXISTS medical_dictionary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL UNIQUE,
    definition TEXT,
    synonyms TEXT, -- JSON array as text, e.g., ["synonym1", "synonym2"]
    is_red_flag INTEGER NOT NULL DEFAULT 0,
    avg_children_count INTEGER DEFAULT 0,
    conflicts_count INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_medical_dictionary_term ON medical_dictionary(term);
CREATE INDEX IF NOT EXISTS idx_medical_dictionary_is_red_flag ON medical_dictionary(is_red_flag);
CREATE INDEX IF NOT EXISTS idx_medical_dictionary_created_at ON medical_dictionary(created_at);
CREATE INDEX IF NOT EXISTS idx_medical_dictionary_updated_at ON medical_dictionary(updated_at);

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS tr_medical_dictionary_touch_on_update
AFTER UPDATE ON medical_dictionary
FOR EACH ROW
BEGIN
    UPDATE medical_dictionary
    SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
    WHERE id = NEW.id;
END;

-- View to show dictionary terms with their tree relationships
CREATE VIEW IF NOT EXISTS v_dictionary_with_tree_info AS
SELECT
    md.id,
    md.term,
    md.definition,
    md.synonyms,
    md.is_red_flag,
    md.avg_children_count,
    md.conflicts_count,
    md.created_at,
    md.updated_at,
    COUNT(DISTINCT n.id) as node_count,
    GROUP_CONCAT(DISTINCT n.depth) as depths,
    GROUP_CONCAT(DISTINCT CASE WHEN n.depth = 0 THEN 'Root'
                               WHEN n.depth = 1 THEN 'Level 1'
                               WHEN n.depth = 2 THEN 'Level 2'
                               WHEN n.depth = 3 THEN 'Level 3'
                               WHEN n.depth = 4 THEN 'Level 4'
                               WHEN n.depth = 5 THEN 'Level 5'
                               WHEN n.depth = 6 THEN 'Level 6'
                               ELSE 'Unknown' END) as depth_labels
FROM medical_dictionary md
LEFT JOIN nodes n ON LOWER(TRIM(md.term)) = LOWER(TRIM(n.label))
GROUP BY md.id, md.term, md.definition, md.synonyms, md.is_red_flag,
         md.avg_children_count, md.conflicts_count, md.created_at, md.updated_at;

-- Function to populate dictionary from existing nodes
-- This will be called by the migration runner to populate initial data
