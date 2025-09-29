-- 016_fix_views_missing_slots_and_no_limits.sql
BEGIN;

-- Drop old views if present
DROP VIEW IF EXISTS v_missing_slots;
DROP VIEW IF EXISTS v_next_incomplete_parent;

-- v_missing_slots: CROSS JOIN slots 1..5 to report all missing numbers
CREATE VIEW v_missing_slots AS
WITH RECURSIVE slots(n) AS (
  SELECT 1 UNION ALL SELECT n+1 FROM slots WHERE n < 5
)
SELECT p.id AS parent_id,
       p.label AS parent_label,
       s.n AS missing_slot
FROM nodes p
JOIN slots s
LEFT JOIN nodes c
  ON c.parent_id = p.id AND c.slot = s.n
WHERE p.parent_id IS NULL OR p.parent_id IS NOT NULL
  AND c.id IS NULL;

-- v_next_incomplete_parent: no LIMIT here; API should limit/order
CREATE VIEW v_next_incomplete_parent AS
WITH cc AS (
  SELECT parent_id, COUNT(*) AS cnt
  FROM nodes
  WHERE parent_id IS NOT NULL
  GROUP BY parent_id
)
SELECT n.id, n.label, n.depth, COALESCE(cc.cnt,0) AS child_count
FROM nodes n
LEFT JOIN cc ON cc.parent_id = n.id
WHERE n.depth BETWEEN 0 AND 4
  AND COALESCE(cc.cnt,0) < 5;

COMMIT;
