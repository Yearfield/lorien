-- Safety: drop any legacy unique index on nodes.label if present
DROP INDEX IF EXISTS idx_nodes_label_unique;
