-- NOTE:
-- This migration name predates the current streamlined codebase.
-- We keep the original filename to preserve migration ordering and
-- compatibility with previously applied databases. The content remains
-- valid and is not tied to any removed feature. Do not rename this file.

-- Performance indexes for conflicts detection
CREATE INDEX IF NOT EXISTS idx_nodes_parent_id ON nodes(parent_id);
CREATE INDEX IF NOT EXISTS idx_nodes_depth_label ON nodes(depth, label);
