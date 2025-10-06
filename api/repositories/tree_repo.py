from typing import List, Dict, Optional, Tuple
import sqlite3
from collections import deque


class TreeRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def next_underfilled_parent(self, after_id: Optional[int] = None) -> Optional[Dict]:
        """Find the next parent with fewer than 5 children, ordered by ID."""
        q = """
        WITH cc AS (
          SELECT parent_id AS id, COUNT(*) AS cnt
          FROM nodes
          WHERE parent_id IS NOT NULL
          GROUP BY parent_id
        )
        SELECT n.id, n.label, n.depth, COALESCE(cc.cnt, 0) AS child_count
        FROM nodes n
        LEFT JOIN cc ON cc.id = n.id
        WHERE n.depth BETWEEN 0 AND 4
          AND COALESCE(cc.cnt, 0) < 5
          AND (? IS NULL OR n.id > ?)
          AND (EXISTS (SELECT 1 FROM nodes WHERE parent_id = n.id LIMIT 1) OR n.depth = 0)
        ORDER BY n.id
        LIMIT 1;
        """
        row = self.conn.execute(q, (after_id, after_id)).fetchone()
        if not row:
            return None
        return {"id": row[0], "label": row[1], "depth": row[2], "child_count": row[3]}

    def next_underfilled_parent_scoped(self, root_id: int, after_id: Optional[int]) -> Optional[Dict]:
        """
        Find the next parent (within the given root subtree) that has <5 children,
        depth between 0 and 4 inclusive. Start after `after_id`; if none, wrap to start.
        """
        # CTE for all nodes under the root
        subtree = """
        WITH RECURSIVE sub(id) AS (
          SELECT ?                -- root_id
          UNION ALL
          SELECT n.id
          FROM nodes n
          JOIN sub s ON n.parent_id = s.id
        ),
        cc AS (
          SELECT parent_id AS id, COUNT(*) AS cnt
      FROM nodes
      WHERE parent_id IS NOT NULL
          GROUP BY parent_id
        )
        """
        base_select = """
        SELECT n.id, n.label, n.depth, COALESCE(cc.cnt,0) AS child_count
        FROM nodes n
        JOIN sub ON sub.id = n.id
        LEFT JOIN cc ON cc.id = n.id
        WHERE n.depth BETWEEN 0 AND 4
          AND COALESCE(cc.cnt,0) < 5
          AND (EXISTS (SELECT 1 FROM nodes WHERE parent_id = n.id LIMIT 1) OR n.depth = 0)
        """

        # Pass 1: after_id cursor
        q1 = f"""{subtree}
        {base_select}
          AND (? IS NULL OR n.id > ?)
        ORDER BY n.id
        LIMIT 1
        """
        row = self.conn.execute(q1, (root_id, after_id, after_id)).fetchone()
        if not row:
            # Pass 2: wrap-around from start
            q2 = f"""{subtree}
            {base_select}
            ORDER BY n.id
            LIMIT 1
            """
            row = self.conn.execute(q2, (root_id,)).fetchone()
        if not row:
            return None
        return {"id": row[0], "label": row[1], "depth": row[2], "child_count": row[3]}

    def set_edge_flag(self, parent_id: int, child_id: int, red_flag: bool) -> None:
        """Set or unset the red flag for a specific parent-child edge."""
        self.conn.execute("""
          INSERT INTO edge_meta(parent_id, child_id, red_flag)
          VALUES(?,?,?)
          ON CONFLICT(parent_id, child_id) DO UPDATE SET red_flag = excluded.red_flag
        """, (parent_id, child_id, 1 if red_flag else 0))

    def list_children(self, parent_id: int, only_red: bool = False) -> List[Dict]:
        """List children of a parent, optionally filtering by red flag status."""
        q = """
        SELECT c.id, c.label, c.depth, c.slot, COALESCE(em.red_flag, 0) as red_flag
        FROM nodes c
        LEFT JOIN edge_meta em ON em.parent_id = ? AND em.child_id = c.id
        WHERE c.parent_id = ?
        ORDER BY c.slot ASC, c.id ASC
        """
        rows = self.conn.execute(q, (parent_id, parent_id)).fetchall()
        items = [{"id": r[0], "label": r[1], "depth": r[2], "slot": r[3], "red_flag": int(r[4]) == 1} for r in rows]
        if only_red:
            items = [it for it in items if it["red_flag"]]
        return items

    def find_clone_candidates_by_label(self, label: str) -> List[Dict]:
        """Find nodes with the given label that have children (potential clone sources)."""
        q = """
        WITH kids AS (SELECT parent_id, COUNT(*) AS cnt FROM nodes WHERE parent_id IS NOT NULL GROUP BY parent_id)
        SELECT n.id, n.label, n.depth, COALESCE(kids.cnt,0) AS child_count
        FROM nodes n
        LEFT JOIN kids ON kids.parent_id = n.id
        WHERE lower(trim(n.label)) = lower(trim(?)) AND COALESCE(kids.cnt,0) > 0
        ORDER BY n.depth ASC, n.id ASC
        """
        return [{"id": r[0], "label": r[1], "depth": r[2], "child_count": r[3]} for r in self.conn.execute(q, (label,))]

    def clone_subtree(self, source_root_id: int, new_parent_id: int) -> int:
        """
        Copy source_root_id and its descendants under new_parent_id, preserving relative order.
        Assign new slots incrementally under each newly created parent.
        Returns number of nodes created (including copied root).
        """
        root_row = self.conn.execute(
            "SELECT id, parent_id, label, depth, slot FROM nodes WHERE id = ?",
            (source_root_id,),
        ).fetchone()
        if not root_row:
            return 0

        dest_row = self.conn.execute(
            "SELECT depth FROM nodes WHERE id = ?",
            (new_parent_id,),
        ).fetchone()
        if not dest_row:
            raise ValueError("dest_parent_not_found")

        dest_depth = dest_row[0]
        if dest_depth >= 5:
            raise ValueError("dest_parent_at_max_depth")

        subtree_rows = self.conn.execute(
            """
            WITH RECURSIVE sub AS (
              SELECT id, parent_id, label, depth, slot FROM nodes WHERE id = ?
              UNION ALL
              SELECT n.id, n.parent_id, n.label, n.depth, n.slot
              FROM nodes n
              JOIN sub s ON n.parent_id = s.id
            )
            SELECT id, parent_id, label, depth, slot
            FROM sub
            ORDER BY parent_id, slot, id
            """,
            (source_root_id,),
        ).fetchall()

        if not subtree_rows:
            return 0

        node_lookup = {row[0]: row for row in subtree_rows}
        source_root_depth = root_row[3]

        # Ensure resulting depths stay within bounds
        for node in subtree_rows:
            offset = node[3] - source_root_depth
            new_depth = dest_depth + 1 + offset
            if new_depth > 6:
                raise ValueError("depth_limit_exceeded")

        # Ensure destination parent has capacity for new immediate children
        existing_children = self.conn.execute(
            "SELECT COUNT(*) FROM nodes WHERE parent_id = ?",
            (new_parent_id,),
        ).fetchone()[0]
        direct_children_to_add = sum(1 for node in subtree_rows if node[1] == source_root_id)
        if existing_children + direct_children_to_add > 5:
            raise ValueError("max_children_exceeded")

        children_map: Dict[int, List[int]] = {}
        for node in subtree_rows:
            parent_id = node[1]
            if parent_id is None:
                continue
            children_map.setdefault(parent_id, []).append(node[0])

        queue = deque([(source_root_id, new_parent_id)])
        created = 0
        child_counts: Dict[int, int] = {new_parent_id: existing_children}

        while queue:
            current_old_id, parent_for_new = queue.popleft()
            node = node_lookup.get(current_old_id)
            if not node:
                continue

            offset = node[3] - source_root_depth
            new_depth = dest_depth + 1 + offset

            current_count = child_counts.get(parent_for_new, 0) + 1
            if current_count > 5:
                raise ValueError("max_children_exceeded")
            child_counts[parent_for_new] = current_count
            slot = current_count

            cursor = self.conn.execute(
                "INSERT INTO nodes (parent_id, depth, slot, label) VALUES (?,?,?,?)",
                (parent_for_new, new_depth, slot, node[2]),
            )
            new_id = cursor.lastrowid
            created += 1

            child_counts[new_id] = 0
            for child_old_id in children_map.get(current_old_id, []):
                queue.append((child_old_id, new_id))

        return created

    def get_ancestors(self, node_id: int):
        """
        Return list of dicts [{id,label,depth}] from root to the given node_id.
        """
        q = """
        WITH RECURSIVE chain AS (
          SELECT id, label, depth, parent_id
          FROM nodes
          WHERE id = ?
          UNION ALL
          SELECT n.id, n.label, n.depth, n.parent_id
          FROM nodes n
          JOIN chain c ON c.parent_id = n.id
        )
        SELECT id, label, depth
        FROM chain
        ORDER BY depth ASC;
        """
        rows = self.conn.execute(q, (node_id,)).fetchall()
        return [{"id": r[0], "label": r[1], "depth": r[2]} for r in rows]
