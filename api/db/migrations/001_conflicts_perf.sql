-- Performance indexes for conflicts detection
-- These indexes help with the variant-sets conflicts engine

-- Index for finding children by parent_id (used in list_children_for_parents)
CREATE INDEX IF NOT EXISTS idx_nodes_parent_id ON nodes(parent_id);

-- Index for grouping parents by depth and label (used in conflicts detection)
CREATE INDEX IF NOT EXISTS idx_nodes_depth_label ON nodes(depth, label);

-- Index for finding parents with exactly 5 children (used in list_parents_with_exact_five)
-- This is a partial index that only includes nodes that are parents
CREATE INDEX IF NOT EXISTS idx_nodes_parents ON nodes(id) WHERE parent_id IS NOT NULL;
