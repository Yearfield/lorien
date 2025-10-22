-- Migration: Add Warhammer engine tables for EngineWarhammer
-- Safe to re-apply (IF NOT EXISTS)
-- Date: 2025-01-27
-- Purpose: Add diseases, symptoms, symptom_disease_conditionals, and warhammer_calculations tables for Bayesian disease probability calculations

-- Diseases table: Store disease names and their estimated lifetime risks
CREATE TABLE IF NOT EXISTS diseases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_name TEXT NOT NULL UNIQUE,
    estimated_lifetime_risk REAL NOT NULL CHECK(estimated_lifetime_risk >= 0.0 AND estimated_lifetime_risk <= 1.0),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Symptoms table: Store symptom names and their base probabilities
CREATE TABLE IF NOT EXISTS symptoms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symptom_name TEXT NOT NULL UNIQUE,
    probability REAL NOT NULL CHECK(probability >= 0.0 AND probability <= 1.0),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Symptom-disease conditionals table: Store P(Symptom|Disease) probabilities
CREATE TABLE IF NOT EXISTS symptom_disease_conditionals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symptom_id INTEGER NOT NULL,
    disease_id INTEGER NOT NULL,
    conditional_probability REAL NOT NULL CHECK(conditional_probability >= 0.0 AND conditional_probability <= 1.0),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    UNIQUE(symptom_id, disease_id),
    FOREIGN KEY (symptom_id) REFERENCES symptoms(id) ON DELETE CASCADE,
    FOREIGN KEY (disease_id) REFERENCES diseases(id) ON DELETE CASCADE
);

-- Warhammer calculations table: Store calculation results and history
CREATE TABLE IF NOT EXISTS warhammer_calculations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    calculation_date TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    input_symptoms TEXT NOT NULL, -- JSON array of symptom names
    results TEXT NOT NULL, -- JSON array of disease results with probabilities
    saved BOOLEAN NOT NULL DEFAULT 0, -- Whether this calculation was explicitly saved
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_diseases_name ON diseases(disease_name);
CREATE INDEX IF NOT EXISTS idx_diseases_created_at ON diseases(created_at);
CREATE INDEX IF NOT EXISTS idx_symptoms_name ON symptoms(symptom_name);
CREATE INDEX IF NOT EXISTS idx_symptoms_created_at ON symptoms(created_at);
CREATE INDEX IF NOT EXISTS idx_conditionals_symptom ON symptom_disease_conditionals(symptom_id);
CREATE INDEX IF NOT EXISTS idx_conditionals_disease ON symptom_disease_conditionals(disease_id);
CREATE INDEX IF NOT EXISTS idx_conditionals_probability ON symptom_disease_conditionals(conditional_probability);
CREATE INDEX IF NOT EXISTS idx_calculations_date ON warhammer_calculations(calculation_date);
CREATE INDEX IF NOT EXISTS idx_calculations_saved ON warhammer_calculations(saved);

-- Trigger to update updated_at timestamp on diseases
CREATE TRIGGER IF NOT EXISTS tr_diseases_touch_on_update
AFTER UPDATE ON diseases
FOR EACH ROW
BEGIN
  UPDATE diseases
  SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE id = NEW.id;
END;

-- Trigger to update updated_at timestamp on symptoms
CREATE TRIGGER IF NOT EXISTS tr_symptoms_touch_on_update
AFTER UPDATE ON symptoms
FOR EACH ROW
BEGIN
  UPDATE symptoms
  SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE id = NEW.id;
END;

-- Trigger to update updated_at timestamp on symptom_disease_conditionals
CREATE TRIGGER IF NOT EXISTS tr_conditionals_touch_on_update
AFTER UPDATE ON symptom_disease_conditionals
FOR EACH ROW
BEGIN
  UPDATE symptom_disease_conditionals
  SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE id = NEW.id;
END;
