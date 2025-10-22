-- Add symptom synonyms table for mapping Warhammer symptoms to decision tree symptoms
CREATE TABLE IF NOT EXISTS symptom_synonyms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    warhammer_symptom TEXT NOT NULL,
    decision_tree_symptom TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(warhammer_symptom, decision_tree_symptom)
);

-- Create indexes for efficient lookups
CREATE INDEX idx_symptom_synonyms_warhammer ON symptom_synonyms(warhammer_symptom);
CREATE INDEX idx_symptom_synonyms_decision_tree ON symptom_synonyms(decision_tree_symptom);

-- Create trigger to update updated_at timestamp
CREATE TRIGGER trg_symptom_synonyms_set_updated_at
AFTER UPDATE ON symptom_synonyms
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE symptom_synonyms
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;
