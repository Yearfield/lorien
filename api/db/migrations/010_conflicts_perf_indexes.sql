-- Performance indexes for conflicts detection
CREATE INDEX IF NOT EXISTS idx_nodes_parent_id ON nodes(parent_id);
CREATE INDEX IF NOT EXISTS idx_nodes_depth_label ON nodes(depth, label);
