-- Migration: Add pathogen tables for EngineShelob
-- Safe to re-apply (IF NOT EXISTS)
-- Date: 2025-01-27
-- Purpose: Add pathogens, association_types, and pathogen_associations tables for pathogen data import

-- Pathogens table: Store pathogen properties and descriptive attributes
CREATE TABLE IF NOT EXISTS pathogens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    classification TEXT,
    nt TEXT,
    pathogen_id TEXT,
    pathogen_name TEXT NOT NULL,
    vaccine TEXT,
    toxin TEXT,
    transmission TEXT,
    ab_resistance TEXT,
    host TEXT,
    commensal TEXT,
    disease TEXT,
    incubation TEXT,
    diagnosis TEXT,
    treatment TEXT,
    prevention TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Association types table: Store unique association names from column headers
CREATE TABLE IF NOT EXISTS association_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Pathogen associations junction table: Link pathogens to associations with binary values
CREATE TABLE IF NOT EXISTS pathogen_associations (
    pathogen_id INTEGER NOT NULL,
    association_type_id INTEGER NOT NULL,
    value INTEGER NOT NULL CHECK(value IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    PRIMARY KEY (pathogen_id, association_type_id),
    FOREIGN KEY (pathogen_id) REFERENCES pathogens(id) ON DELETE CASCADE,
    FOREIGN KEY (association_type_id) REFERENCES association_types(id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_pathogens_name ON pathogens(pathogen_name);
CREATE INDEX IF NOT EXISTS idx_pathogens_classification ON pathogens(classification);
CREATE INDEX IF NOT EXISTS idx_pathogens_created_at ON pathogens(created_at);
CREATE INDEX IF NOT EXISTS idx_association_types_name ON association_types(name);
CREATE INDEX IF NOT EXISTS idx_pathogen_associations_pathogen ON pathogen_associations(pathogen_id);
CREATE INDEX IF NOT EXISTS idx_pathogen_associations_type ON pathogen_associations(association_type_id);
CREATE INDEX IF NOT EXISTS idx_pathogen_associations_value ON pathogen_associations(value);

-- Trigger to update updated_at timestamp on pathogens
CREATE TRIGGER IF NOT EXISTS tr_pathogens_touch_on_update
AFTER UPDATE ON pathogens
FOR EACH ROW
BEGIN
  UPDATE pathogens
  SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE id = NEW.id;
END;

-- Trigger to update updated_at timestamp on pathogen_associations
CREATE TRIGGER IF NOT EXISTS tr_pathogen_associations_touch_on_update
AFTER UPDATE ON pathogen_associations
FOR EACH ROW
BEGIN
  UPDATE pathogen_associations
  SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now')
  WHERE pathogen_id = NEW.pathogen_id AND association_type_id = NEW.association_type_id;
END;
