-- Optimized SQLite schema for decision tree application
-- Enhanced with comprehensive indexing strategy for improved performance

-- ---- Connection pragmas (optimized for performance)
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;  -- 64MB cache
PRAGMA temp_store = MEMORY;
PRAGMA mmap_size = 268435456;  -- 256MB memory mapping
PRAGMA optimize;  -- Optimize database

-- ---- TABLES ----

-- Nodes table: each row is a node in the tree
CREATE TABLE IF NOT EXISTS nodes (
    id         INTEGER PRIMARY KEY,
    parent_id  INTEGER NULL REFERENCES nodes(id) ON DELETE CASCADE,
    depth      INTEGER NOT NULL CHECK (depth BETWEEN 0 AND 6),   -- 0=root (Vital Measurement)
    slot       INTEGER NULL CHECK (
                   (parent_id IS NULL AND slot IS NULL AND depth = 0) OR
                   (parent_id IS NOT NULL AND slot IS NOT NULL AND slot >= 1 AND depth BETWEEN 1 AND 6)
               ),
    label      TEXT    NOT NULL,
    is_leaf    INTEGER NOT NULL DEFAULT 0,                       -- convenience flag (depth>=5)
    created_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    CHECK ( (depth = 0 AND parent_id IS NULL) OR (depth > 0 AND parent_id IS NOT NULL) )
);

-- Triage per leaf node only (depth>=5)
CREATE TABLE IF NOT EXISTS triage (
    node_id           INTEGER PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
    diagnostic_triage TEXT,     -- nullable; can be edited later
    actions           TEXT,     -- nullable
    created_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
    updated_at        TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Red flags catalogue
CREATE TABLE IF NOT EXISTS red_flags (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    severity    TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    created_at  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Tree parent version tracking for optimistic concurrency
CREATE TABLE IF NOT EXISTS tree_parent_version (
    parent_id  INTEGER PRIMARY KEY REFERENCES nodes(id) ON DELETE CASCADE,
    version    INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- Audit log for red flag assignments
CREATE TABLE IF NOT EXISTS red_flag_audit (
    id         INTEGER PRIMARY KEY,
    node_id    INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    flag_id    INTEGER NOT NULL REFERENCES red_flags(id) ON DELETE CASCADE,
    action     TEXT NOT NULL CHECK (action IN ('assigned', 'removed')),
    timestamp  TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now'))
);

-- ---- PERFORMANCE OPTIMIZED INDEXES ----

-- Core tree navigation indexes
CREATE INDEX IF NOT EXISTS idx_nodes_parent_id ON nodes(parent_id) WHERE parent_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_nodes_depth ON nodes(depth);
CREATE INDEX IF NOT EXISTS idx_nodes_parent_slot ON nodes(parent_id, slot) WHERE parent_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_nodes_is_leaf ON nodes(is_leaf);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_nodes_depth_parent ON nodes(depth, parent_id);
CREATE INDEX IF NOT EXISTS idx_nodes_parent_depth ON nodes(parent_id, depth);
CREATE INDEX IF NOT EXISTS idx_nodes_label_search ON nodes(label COLLATE NOCASE);

-- Time-based indexes for audit and tracking
CREATE INDEX IF NOT EXISTS idx_nodes_created_at ON nodes(created_at);
CREATE INDEX IF NOT EXISTS idx_nodes_updated_at ON nodes(updated_at);
CREATE INDEX IF NOT EXISTS idx_triage_updated_at ON triage(updated_at);
CREATE INDEX IF NOT EXISTS idx_red_flag_audit_timestamp ON red_flag_audit(timestamp);
CREATE INDEX IF NOT EXISTS idx_red_flag_audit_node_id ON red_flag_audit(node_id);

-- Triage and red flags indexes
CREATE INDEX IF NOT EXISTS idx_triage_node_id ON triage(node_id);
CREATE INDEX IF NOT EXISTS idx_red_flags_severity ON red_flags(severity);
CREATE INDEX IF NOT EXISTS idx_red_flags_name ON red_flags(name COLLATE NOCASE);

-- Version tracking indexes
CREATE INDEX IF NOT EXISTS idx_parent_version_parent_id ON tree_parent_version(parent_id);

-- ---- COVERING INDEXES FOR COMMON QUERIES ----

-- Covering index for children queries (includes all commonly accessed columns)
CREATE INDEX IF NOT EXISTS idx_nodes_children_covering ON nodes(parent_id, slot, id, label, depth, is_leaf) 
WHERE parent_id IS NOT NULL;

-- Covering index for depth-based queries
CREATE INDEX IF NOT EXISTS idx_nodes_depth_covering ON nodes(depth, id, label, parent_id, is_leaf);

-- Covering index for leaf node queries
CREATE INDEX IF NOT EXISTS idx_nodes_leaf_covering ON nodes(is_leaf, id, label, parent_id, depth) 
WHERE is_leaf = 1;

-- ---- PARTIAL INDEXES FOR OPTIMIZATION ----

-- Index for incomplete parents (depth < 5 with < 5 children)
CREATE INDEX IF NOT EXISTS idx_nodes_incomplete_parents ON nodes(id, depth, parent_id) 
WHERE depth < 5 AND parent_id IS NOT NULL;

-- Index for root nodes only
CREATE INDEX IF NOT EXISTS idx_nodes_root ON nodes(id, label) WHERE depth = 0;

-- Index for non-leaf nodes
CREATE INDEX IF NOT EXISTS idx_nodes_non_leaf ON nodes(id, parent_id, depth) WHERE is_leaf = 0;

-- ---- TRIGGERS FOR PERFORMANCE AND DATA INTEGRITY ----

-- Trigger to update is_leaf flag automatically
CREATE TRIGGER IF NOT EXISTS update_is_leaf_trigger
    AFTER INSERT OR UPDATE OF depth ON nodes
    FOR EACH ROW
    BEGIN
        UPDATE nodes SET is_leaf = (NEW.depth >= 5) WHERE id = NEW.id;
    END;

-- Trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_timestamp_trigger
    AFTER UPDATE ON nodes
    FOR EACH ROW
    BEGIN
        UPDATE nodes SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE id = NEW.id;
    END;

-- Trigger to update triage timestamp
CREATE TRIGGER IF NOT EXISTS update_triage_timestamp_trigger
    AFTER UPDATE ON triage
    FOR EACH ROW
    BEGIN
        UPDATE triage SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ','now') WHERE node_id = NEW.node_id;
    END;

-- Trigger to maintain parent version on node changes
CREATE TRIGGER IF NOT EXISTS update_parent_version_trigger
    AFTER INSERT OR UPDATE OR DELETE ON nodes
    FOR EACH ROW
    BEGIN
        -- Update parent version when children change
        IF OLD.parent_id IS NOT NULL THEN
            INSERT OR REPLACE INTO tree_parent_version (parent_id, version, updated_at)
            VALUES (OLD.parent_id, COALESCE((SELECT version FROM tree_parent_version WHERE parent_id = OLD.parent_id), 0) + 1, strftime('%Y-%m-%dT%H:%M:%fZ','now'));
        END IF;
        
        IF NEW.parent_id IS NOT NULL AND (OLD.parent_id IS NULL OR OLD.parent_id != NEW.parent_id) THEN
            INSERT OR REPLACE INTO tree_parent_version (parent_id, version, updated_at)
            VALUES (NEW.parent_id, COALESCE((SELECT version FROM tree_parent_version WHERE parent_id = NEW.parent_id), 0) + 1, strftime('%Y-%m-%dT%H:%M:%fZ','now'));
        END IF;
    END;

-- ---- VIEWS FOR COMMON QUERIES ----

-- View for complete node information with parent details
CREATE VIEW IF NOT EXISTS nodes_with_parent AS
SELECT 
    n.id,
    n.parent_id,
    n.depth,
    n.slot,
    n.label,
    n.is_leaf,
    n.created_at,
    n.updated_at,
    p.label as parent_label,
    p.depth as parent_depth
FROM nodes n
LEFT JOIN nodes p ON n.parent_id = p.id;

-- View for incomplete parents (those with < 5 children)
CREATE VIEW IF NOT EXISTS incomplete_parents AS
SELECT 
    n.id,
    n.label,
    n.depth,
    n.parent_id,
    COUNT(c.id) as child_count,
    (5 - COUNT(c.id)) as slots_available
FROM nodes n
LEFT JOIN nodes c ON n.id = c.parent_id
WHERE n.depth < 5 AND n.parent_id IS NOT NULL
GROUP BY n.id, n.label, n.depth, n.parent_id
HAVING COUNT(c.id) < 5
ORDER BY n.id;

-- View for tree statistics
CREATE VIEW IF NOT EXISTS tree_stats AS
SELECT 
    COUNT(*) as total_nodes,
    COUNT(CASE WHEN depth = 0 THEN 1 END) as root_nodes,
    COUNT(CASE WHEN is_leaf = 1 THEN 1 END) as leaf_nodes,
    COUNT(CASE WHEN is_leaf = 0 THEN 1 END) as internal_nodes,
    COUNT(DISTINCT parent_id) as parent_nodes,
    COUNT(DISTINCT depth) as depth_levels,
    MIN(depth) as min_depth,
    MAX(depth) as max_depth
FROM nodes;

-- View for node hierarchy (for tree traversal)
CREATE VIEW IF NOT EXISTS node_hierarchy AS
WITH RECURSIVE node_tree AS (
    -- Base case: root nodes
    SELECT 
        id,
        parent_id,
        depth,
        slot,
        label,
        is_leaf,
        0 as level,
        CAST(id AS TEXT) as path
    FROM nodes 
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Recursive case: child nodes
    SELECT 
        n.id,
        n.parent_id,
        n.depth,
        n.slot,
        n.label,
        n.is_leaf,
        nt.level + 1,
        nt.path || '.' || CAST(n.id AS TEXT)
    FROM nodes n
    JOIN node_tree nt ON n.parent_id = nt.id
)
SELECT * FROM node_tree ORDER BY path;

-- ---- QUERY OPTIMIZATION HINTS ----

-- Analyze tables for query optimizer
ANALYZE;

-- Set query optimizer hints
PRAGMA optimize;

-- ---- PERFORMANCE MONITORING QUERIES ----

-- Query to check index usage (run periodically)
-- SELECT name, sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL;

-- Query to check table sizes
-- SELECT name, (SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=m.name) as row_count 
-- FROM sqlite_master m WHERE type='table';

-- Query to check WAL file size
-- PRAGMA journal_mode;

-- Query to check cache hit ratio (requires custom implementation)
-- PRAGMA cache_size;
