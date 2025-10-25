-- Migration: Add ShortBow engine tables for EngineShortBow
-- Safe to re-apply (IF NOT EXISTS)
-- Date: 2025-01-27
-- Purpose: Add symptoms, symptom_links, and calculations tables for interactive symptom navigation

-- ShortBow symptoms table: Store symptom names
CREATE TABLE IF NOT EXISTS shortbow_symptoms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symptom_name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- ShortBow symptom links table: Store probability matrix data
CREATE TABLE IF NOT EXISTS shortbow_symptom_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symptom_from_id INTEGER NOT NULL,
    symptom_to_id INTEGER NOT NULL,
    probability REAL NOT NULL CHECK(probability >= 0.0 AND probability <= 1.0),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    UNIQUE(symptom_from_id, symptom_to_id),
    FOREIGN KEY (symptom_from_id) REFERENCES shortbow_symptoms(id) ON DELETE CASCADE,
    FOREIGN KEY (symptom_to_id) REFERENCES shortbow_symptoms(id) ON DELETE CASCADE
);

-- ShortBow calculations table: Store navigation session results
CREATE TABLE IF NOT EXISTS shortbow_calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    calculation_date TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    initial_symptom TEXT NOT NULL,
    selected_symptoms TEXT NOT NULL, -- JSON array of selected symptoms
    saved BOOLEAN NOT NULL DEFAULT 0, -- Whether this calculation was explicitly saved
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_shortbow_symptoms_name ON shortbow_symptoms(symptom_name);
CREATE INDEX IF NOT EXISTS idx_shortbow_symptoms_created_at ON shortbow_symptoms(created_at);
CREATE INDEX IF NOT EXISTS idx_shortbow_links_from ON shortbow_symptom_links(symptom_from_id);
CREATE INDEX IF NOT EXISTS idx_shortbow_links_to ON shortbow_symptom_links(symptom_to_id);
CREATE INDEX IF NOT EXISTS idx_shortbow_links_probability ON shortbow_symptom_links(probability);
CREATE INDEX IF NOT EXISTS idx_shortbow_calculations_date ON shortbow_calculations(calculation_date);
CREATE INDEX IF NOT EXISTS idx_shortbow_calculations_saved ON shortbow_calculations(saved);

-- Trigger to update updated_at timestamp on shortbow_symptoms
CREATE TRIGGER IF NOT EXISTS tr_shortbow_symptoms_touch_on_update
AFTER UPDATE ON shortbow_symptoms
FOR EACH ROW
BEGIN
  UPDATE shortbow_symptoms
  SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE id = NEW.id;
END;

-- Trigger to update updated_at timestamp on shortbow_symptom_links
CREATE TRIGGER IF NOT EXISTS tr_shortbow_links_touch_on_update
AFTER UPDATE ON shortbow_symptom_links
FOR EACH ROW
BEGIN
  UPDATE shortbow_symptom_links
  SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE id = NEW.id;
END;
