-- Migration: Add dictionary_terms table and node_terms association table
-- Date: 2025-01-01
-- Purpose: Add dictionary administration tables for medical terms

CREATE TABLE IF NOT EXISTS dictionary_terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    label TEXT NOT NULL,
    category TEXT NOT NULL,
    code TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    UNIQUE(label, category),
    UNIQUE(code)
);

-- Node-Term associations (many-to-many)
CREATE TABLE IF NOT EXISTS node_terms (
    node_id INTEGER NOT NULL,
    term_id INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (node_id, term_id),
    FOREIGN KEY (node_id) REFERENCES nodes(id) ON DELETE CASCADE,
    FOREIGN KEY (term_id) REFERENCES dictionary_terms(id) ON DELETE RESTRICT
);

-- Parent versioning for optimistic concurrency
CREATE TABLE IF NOT EXISTS tree_parent_version (
    parent_id INTEGER PRIMARY KEY,
    version INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_dictionary_label ON dictionary_terms(label);
CREATE INDEX IF NOT EXISTS idx_dictionary_category ON dictionary_terms(category);
CREATE INDEX IF NOT EXISTS idx_dictionary_code ON dictionary_terms(code);
CREATE INDEX IF NOT EXISTS idx_dictionary_created_at ON dictionary_terms(created_at);
CREATE INDEX IF NOT EXISTS idx_dictionary_updated_at ON dictionary_terms(updated_at);
CREATE INDEX IF NOT EXISTS idx_node_terms_node_id ON node_terms(node_id);
CREATE INDEX IF NOT EXISTS idx_node_terms_term_id ON node_terms(term_id);

-- Fast parent-child lookups
CREATE INDEX IF NOT EXISTS idx_nodes_parent_slot ON nodes(parent_id, slot);

-- Note: Unique index for duplicate child labels will be added manually
-- after verifying no existing data conflicts

-- Note: Parent version bump trigger will be created manually
-- after verifying the nodes table schema and data
