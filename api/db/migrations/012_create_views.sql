-- 012_create_views.sql
BEGIN TRANSACTION;

-- Parents with exactly 5 direct children (still valid for conflicts engine)
CREATE VIEW IF NOT EXISTS v_parents_exact_5 AS
SELECT
  p.id AS parent_id,
  COUNT(c.id) AS child_count,
  GROUP_CONCAT(c.label, ', ') AS children
FROM nodes p
LEFT JOIN nodes c ON c.parent_id = p.id
WHERE p.depth BETWEEN 0 AND 4
GROUP BY p.id
HAVING child_count = 5;

-- Missing slots (optional diagnostic; harmless with relaxed limit)
-- Keep if still referenced by Data Quality; otherwise safe to leave here.
CREATE VIEW IF NOT EXISTS v_missing_slots AS
SELECT
  p.id AS parent_id,
  TRIM(
    GROUP_CONCAT(
      CASE
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 1) THEN '1'
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 2) THEN '2'
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 3) THEN '3'
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 4) THEN '4'
        WHEN NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = p.id AND c.slot = 5) THEN '5'
        ELSE NULL
      END, ', '
    )
  ) AS missing_slots
FROM nodes p
WHERE p.parent_id IS NOT NULL
GROUP BY p.id;

-- Tree coverage summary (unchanged, utility view)
CREATE VIEW IF NOT EXISTS v_tree_coverage AS
SELECT
  depth,
  COUNT(*) AS total_nodes,
  SUM(CASE WHEN depth = 5 THEN 1 ELSE 0 END) AS leaves
FROM nodes
GROUP BY depth
ORDER BY depth;

-- Next incomplete parent (utility view)
CREATE VIEW IF NOT EXISTS v_next_incomplete_parent AS
SELECT
  p.id,
  p.label,
  p.depth,
  COUNT(c.id) AS child_count
FROM nodes p
LEFT JOIN nodes c ON c.parent_id = p.id
WHERE p.depth < 5
GROUP BY p.id, p.label, p.depth
HAVING child_count < 5
ORDER BY p.depth, p.id
LIMIT 1;

-- Paths complete (utility view)
CREATE VIEW IF NOT EXISTS v_paths_complete AS
SELECT
  p.id,
  p.label,
  p.depth,
  CASE WHEN p.depth = 5 THEN 1 ELSE 0 END AS is_leaf
FROM nodes p
WHERE p.depth = 5;

COMMIT;
