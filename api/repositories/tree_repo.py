from typing import Optional, Tuple, Dict, Any, List
import sqlite3
import math
from api.db import get_conn, ensure_schema, tx
from collections import defaultdict
from api.repositories.validators import ensure_unique_5

CANON_HEADERS = [
    "Vital Measurement","Node 1","Node 2","Node 3","Node 4","Node 5",
    "Diagnostic Triage","Actions"
]

def _norm(s: str) -> str:
    return (s or "").strip()

def sanitize_label(val) -> str | None:
    """Central sanitization for all label values."""
    if val is None: return None
    s = str(val).strip()
    if s == "" or s.lower() == "nan":
        return None
    return s

def create_root_if_missing(conn, label: str) -> int:
    """Create root with label if not exists, return id."""
    lab = sanitize_label(label)
    if not lab:
        raise ValueError("empty_root_label")
    row = conn.execute("SELECT id FROM nodes WHERE parent_id IS NULL AND label=?", (lab,)).fetchone()
    if row: return int(row["id"])
    cur = conn.execute("INSERT INTO nodes(parent_id,label,depth,slot) VALUES (NULL,?,0,NULL)", (lab,))
    return int(cur.lastrowid)

def _is_blank_label(val) -> bool:
    """Check if a label value is blank, None, or NaN."""
    return sanitize_label(val) is None

def _first_free_slot(conn: sqlite3.Connection, parent_id: int) -> Optional[int]:
    cur = conn.execute("SELECT slot FROM nodes WHERE parent_id=? ORDER BY slot", (parent_id,))
    used = {r["slot"] for r in cur.fetchall() if r["slot"] is not None}
    for k in (1,2,3,4,5):
        if k not in used:
            return k
    return None

def get_or_create_root(conn: sqlite3.Connection, label: str) -> int:
    label = _norm(label)
    cur = conn.execute("SELECT id FROM nodes WHERE parent_id IS NULL AND depth=0 AND label=?", (label,))
    row = cur.fetchone()
    if row: return row["id"]
    cur = conn.execute(
        "INSERT INTO nodes (parent_id,label,depth,slot) VALUES (NULL,?,0,NULL)",
        (label,)
    )
    return cur.lastrowid

def get_or_create_child(conn: sqlite3.Connection, parent_id: int, label: str, depth: int) -> Tuple[Optional[int], bool, bool]:
    """
    Returns (node_id, created, skipped_overfull)
    """
    label = _norm(label)
    cur = conn.execute("SELECT id FROM nodes WHERE parent_id=? AND label=? AND depth=?", (parent_id, label, depth))
    row = cur.fetchone()
    if row:
        return row["id"], False, False

    slot = _first_free_slot(conn, parent_id)
    if slot is None:
        # parent already has 5 children — never create >5
        return None, False, True

    cur = conn.execute(
        "INSERT OR IGNORE INTO nodes (parent_id,label,depth,slot) VALUES (?,?,?,?)",
        (parent_id, label, depth, slot)
    )
    if cur.rowcount == 0:
        # race: try to fetch again
        cur2 = conn.execute("SELECT id FROM nodes WHERE parent_id=? AND label=? AND depth=?", (parent_id, label, depth))
        row2 = cur2.fetchone()
        return (row2["id"] if row2 else None), False, False

    return cur.lastrowid, True, False

def upsert_outcome(conn: sqlite3.Connection, node_id: int, triage: str, actions: str) -> Tuple[bool, bool]:
    """
    Returns (created, updated)
    """
    triage, actions = _norm(triage), _norm(actions)
    cur = conn.execute("SELECT node_id FROM outcomes WHERE node_id=?", (node_id,))
    if cur.fetchone():
        conn.execute("UPDATE outcomes SET diagnostic_triage=?, actions=? WHERE node_id=?", (triage, actions, node_id))
        return (False, True)
    conn.execute("INSERT INTO outcomes (node_id, diagnostic_triage, actions) VALUES (?,?,?)", (node_id, triage, actions))
    return (True, False)

def stats(conn: sqlite3.Connection) -> Dict[str, int]:
    nodes = conn.execute("SELECT COUNT(*) AS c FROM nodes").fetchone()["c"]
    roots = conn.execute("SELECT COUNT(*) AS c FROM nodes WHERE depth=0").fetchone()["c"]
    leaves = conn.execute("""
        SELECT COUNT(*) AS c
        FROM nodes n
        WHERE NOT EXISTS (SELECT 1 FROM nodes c WHERE c.parent_id = n.id)
    """).fetchone()["c"]
    # A "complete path" is any path reaching depth 5; depth=5 nodes are terminals by constraint
    complete_paths = conn.execute("SELECT COUNT(*) AS c FROM nodes WHERE depth=5").fetchone()["c"]
    # Incomplete parents = any node with <5 children (including 0)
    incomplete_parents = conn.execute("""
        SELECT COUNT(*) AS c FROM (
          SELECT p.id
          FROM nodes p
          LEFT JOIN nodes c ON c.parent_id = p.id
          GROUP BY p.id
          HAVING COUNT(c.id) < 5
        ) t
    """).fetchone()["c"]

    return {
        "nodes": int(nodes),
        "roots": int(roots),
        "leaves": int(leaves),
        "complete_paths": int(complete_paths),
        "incomplete_parents": int(incomplete_parents)
    }

def import_dataframe(conn: sqlite3.Connection, df) -> Dict[str, Any]:
    """
    Transactionally import a canonical dataframe into nodes/outcomes
    """
    ensure_schema(conn)
    created_roots = 0
    created_nodes = 0
    updated_nodes = 0  # (no-op in this phase, reserved)
    created_outcomes = 0
    updated_outcomes = 0
    skipped_overfull = 0
    rows_processed = 0

    with tx(conn):
        for _, row in df.iterrows():
            # Sanitize root label
            root_label = sanitize_label(row.get("Vital Measurement"))
            if not root_label:
                continue  # skip row if no valid root
            parent_id = create_root_if_missing(conn, root_label)
            # Count root creation by checking immediate existence delta is tricky; we tolerate approximate:
            # treat as creation if no prior path existed at this moment (optional). We skip root count accuracy here.
            # (We'll count nodes via stats for acceptance instead.)

            # Walk levels
            last_node_id = parent_id
            depth = 0
            child_count = 0
            for i, col in enumerate(["Node 1","Node 2","Node 3","Node 4","Node 5"], start=1):
                lab = sanitize_label(row.get(col))
                if not lab:
                    break  # stop deeper creation at first blank
                node_id, created, skipped = get_or_create_child(conn, last_node_id, lab, i)
                if skipped:
                    skipped_overfull += 1
                    break  # cannot go deeper if parent is overfull
                last_node_id = node_id
                depth = i
                child_count += 1
                if created: created_nodes += 1

            # Outcomes at the last realized node in path (if any outcome present)
            triage = sanitize_label(row.get("Diagnostic Triage"))
            actions = sanitize_label(row.get("Actions"))
            if last_node_id is not None and (triage or actions):
                c, u = upsert_outcome(conn, last_node_id, triage, actions)
                if c: created_outcomes += 1
                if u: updated_outcomes += 1

            rows_processed += 1

    return {
        "status": "success",
        "rows_processed": rows_processed,
        "created": {"roots": created_roots, "nodes": created_nodes},
        "updated": {"nodes": updated_nodes, "outcomes": updated_outcomes},
        "skipped": {"overfull_parents": skipped_overfull}
    }

def export_rows(conn: sqlite3.Connection, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """
    Reconstruct rows in the canonical 8-column shape from persisted nodes + outcomes.
    A row represents the path from a root to:
      - any leaf (no children), OR
      - any node explicitly having an outcome.
    """
    # Recursive CTE to build paths and pivot depths into columns
    base_cte = """
    WITH RECURSIVE chain AS (
      SELECT
        id, parent_id, label, depth,
        label AS root_label,
        NULL AS n1, NULL AS n2, NULL AS n3, NULL AS n4, NULL AS n5
      FROM nodes
      WHERE depth = 0
      UNION ALL
      SELECT
        c.id, c.parent_id, c.label, c.depth,
        chain.root_label,
        CASE WHEN c.depth = 1 THEN c.label ELSE chain.n1 END AS n1,
        CASE WHEN c.depth = 2 THEN c.label ELSE chain.n2 END AS n2,
        CASE WHEN c.depth = 3 THEN c.label ELSE chain.n3 END AS n3,
        CASE WHEN c.depth = 4 THEN c.label ELSE chain.n4 END AS n4,
        CASE WHEN c.depth = 5 THEN c.label ELSE chain.n5 END AS n5
      FROM nodes c
      JOIN chain ON c.parent_id = chain.id
    )
    """

    rows_sql = f"""
    {base_cte}
    SELECT
      chain.root_label AS "Vital Measurement",
      chain.n1 AS "Node 1",
      chain.n2 AS "Node 2",
      chain.n3 AS "Node 3",
      chain.n4 AS "Node 4",
      chain.n5 AS "Node 5",
      COALESCE(o.diagnostic_triage, '') AS "Diagnostic Triage",
      COALESCE(o.actions, '') AS "Actions"
    FROM chain
    LEFT JOIN outcomes o ON o.node_id = chain.id
    WHERE
      -- Show terminal paths or nodes that explicitly have outcomes
      (NOT EXISTS (SELECT 1 FROM nodes k WHERE k.parent_id = chain.id))
      OR o.node_id IS NOT NULL
    ORDER BY
      "Vital Measurement" ASC,
      "Node 1" ASC,
      "Node 2" ASC,
      "Node 3" ASC,
      "Node 4" ASC,
      "Node 5" ASC
    LIMIT ? OFFSET ?;
    """

    total_sql = f"""
    {base_cte}
    SELECT COUNT(*)
    FROM (
      SELECT chain.id
      FROM chain
      LEFT JOIN outcomes o ON o.node_id = chain.id
      WHERE
        (NOT EXISTS (SELECT 1 FROM nodes k WHERE k.parent_id = chain.id))
        OR o.node_id IS NOT NULL
    ) t;
    """

    cur_total = conn.execute(total_sql)
    total = int(cur_total.fetchone()[0])

    cur = conn.execute(rows_sql, (int(limit), int(offset)))
    items: List[Dict[str, Any]] = []
    for r in cur.fetchall():
        items.append({
            "Vital Measurement": r["Vital Measurement"],
            "Node 1": r["Node 1"],
            "Node 2": r["Node 2"],
            "Node 3": r["Node 3"],
            "Node 4": r["Node 4"],
            "Node 5": r["Node 5"],
            "Diagnostic Triage": r["Diagnostic Triage"],
            "Actions": r["Actions"],
        })
    return {"items": items, "total": total, "limit": int(limit), "offset": int(offset)}

def missing_slots(conn: sqlite3.Connection, limit: int, offset: int, depth: Optional[int] = None, q: Optional[str] = None) -> Dict[str, Any]:
    where = []
    params: List[Any] = []
    if depth is not None:
        where.append("p.depth = ?")
        params.append(int(depth))
    if q:
        where.append("LOWER(p.label) LIKE ?")
        params.append(f"%{q.lower()}%")

    base = """
      SELECT p.id AS parent_id, p.label, p.depth, GROUP_CONCAT(c.slot) AS used
      FROM nodes p
      LEFT JOIN nodes c ON c.parent_id = p.id
    """
    if where:
        base += " WHERE " + " AND ".join(where)
    group_having = " GROUP BY p.id HAVING COUNT(c.id) < 5 "
    order_by = " ORDER BY p.depth ASC, p.label ASC, p.id ASC "

    total_sql = "SELECT COUNT(*) FROM (" + base + group_having + ") t"
    items_sql = base + group_having + order_by + " LIMIT ? OFFSET ?"

    total = int(conn.execute(total_sql, params).fetchone()[0])
    cur = conn.execute(items_sql, params + [int(limit), int(offset)])

    items: List[Dict[str, Any]] = []
    for r in cur.fetchall():
        used_set = set()
        if r["used"]:
            for s in str(r["used"]).split(","):
                try:
                    used_set.add(int(s))
                except Exception:
                    pass
        missing = [k for k in (1,2,3,4,5) if k not in used_set]
        items.append({
            "parent_id": r["parent_id"],
            "label": r["label"],
            "depth": int(r["depth"]),
            "missing_slots": missing
        })

    return {"items": items, "total": total, "limit": int(limit), "offset": int(offset)}

def next_incomplete_parent(conn: sqlite3.Connection) -> Optional[Dict[str, Any]]:
    """
    Return the next incomplete parent by ascending depth, then label, then id.
    Uses the same logic as missing_slots(limit=1).
    """
    sql = """
    SELECT p.id AS parent_id, p.label, p.depth,
           GROUP_CONCAT(c.slot) AS used
    FROM nodes p
    LEFT JOIN nodes c ON c.parent_id = p.id
    GROUP BY p.id
    HAVING COUNT(c.id) < 5
    ORDER BY p.depth ASC, p.label ASC, p.id ASC
    LIMIT 1;
    """
    row = conn.execute(sql).fetchone()
    if not row:
        return None
    used = set()
    if row["used"]:
        for s in str(row["used"]).split(","):
            try:
                used.add(int(s))
            except Exception:
                pass
    missing = [k for k in (1,2,3,4,5) if k not in used]
    return {
        "parent_id": row["parent_id"],
        "label": row["label"],
        "depth": int(row["depth"]),
        "missing_slots": missing
    }

def list_parents(conn: sqlite3.Connection, limit: int = 50, offset: int = 0,
                 incomplete_only: bool = True, depth: Optional[int] = None,
                 q: Optional[str] = None) -> Dict[str, Any]:
    """List parents with optional filtering and pagination."""
    where, params = [], []
    if depth is not None:
        where.append("p.depth = ?")
        params.append(int(depth))
    if q:
        where.append("LOWER(p.label) LIKE ?")
        params.append(f"%{q.lower()}%")
    
    base = """
      SELECT p.id AS parent_id, p.label, p.depth, COUNT(c.id) AS child_count,
             GROUP_CONCAT(c.slot) AS used
      FROM nodes p
      LEFT JOIN nodes c ON c.parent_id = p.id
    """
    if where:
        base += " WHERE " + " AND ".join(where)
    base += " GROUP BY p.id "
    if incomplete_only:
        base += " HAVING COUNT(c.id) < 5 "
    
    total_sql = "SELECT COUNT(*) FROM (" + base + ") t"
    items_sql = base + " ORDER BY p.depth ASC, p.label ASC, p.id ASC LIMIT ? OFFSET ?"
    
    total = int(conn.execute(total_sql, params).fetchone()[0])
    cur = conn.execute(items_sql, params + [int(limit), int(offset)])
    
    items: List[Dict[str, Any]] = []
    for r in cur.fetchall():
        used = set()
        if r["used"]:
            for s in str(r["used"]).split(","):
                try:
                    used.add(int(s))
                except:
                    pass
        missing = [k for k in (1,2,3,4,5) if k not in used]
        items.append({
            "parent_id": r["parent_id"],
            "label": r["label"],
            "depth": int(r["depth"]),
            "child_count": int(r["child_count"]),
            "missing_slots": missing
        })
    
    return {"items": items, "total": total, "limit": int(limit), "offset": int(offset)}

def list_children(conn: sqlite3.Connection, parent_id: int) -> Dict[str, Any]:
    """List children of a specific parent."""
    prow = conn.execute("SELECT id, label, depth FROM nodes WHERE id=?", (parent_id,)).fetchone()
    if not prow:
        return {"parent": None, "children": []}
    
    cur = conn.execute("SELECT id, slot, label, depth FROM nodes WHERE parent_id=? ORDER BY slot", (parent_id,))
    children = [{"id": r["id"], "slot": r["slot"], "label": r["label"], "depth": r["depth"]} for r in cur.fetchall()]
    
    return {
        "parent": {"id": prow["id"], "label": prow["label"], "depth": prow["depth"]},
        "children": children
    }

def put_slot_label(conn: sqlite3.Connection, parent_id: int, slot: int, label: str) -> Dict[str, Any]:
    """
    Create/update/move a child under parent_id to occupy `slot` with `label`.
    Rules:
      - slot must be 1..5
      - parent must exist and depth < 5
      - if slot occupied by different label -> 409 (no silent overwrite)
      - if same label exists under parent in another slot:
          - if target slot empty -> move (update its slot)
          - if target slot occupied by different label -> 409
      - else create child at (parent_id, slot) with depth=parent.depth+1
    Returns: { action: "created"|"updated"|"moved"|"noop", node_id, parent_id, slot, label }
    """
    if slot < 1 or slot > 5:
        raise ValueError("slot_out_of_range")

    # Validate parent
    prow = conn.execute("SELECT id, depth FROM nodes WHERE id=?", (parent_id,)).fetchone()
    if not prow:
        raise LookupError("parent_not_found")
    parent_depth = int(prow["depth"])
    if parent_depth >= 5:
        raise ValueError("parent_at_max_depth")

    new_depth = parent_depth + 1

    with tx(conn):
        # Current occupant of requested slot?
        occ = conn.execute("SELECT id, label FROM nodes WHERE parent_id=? AND slot=?", (parent_id, slot)).fetchone()
        if occ:
            # Same label? -> noop
            if occ["label"] == label:
                return {"action": "noop", "node_id": int(occ["id"]), "parent_id": parent_id, "slot": slot, "label": label}
            # Different label occupies slot -> 409 scenario (handled by router catching IntegrityError OR we raise)
            # But first, check if the same label exists elsewhere to potentially move (only if we can free the slot)
            existing = conn.execute("SELECT id, slot FROM nodes WHERE parent_id=? AND label=?", (parent_id, label)).fetchone()
            if existing:
                # Slot already taken by other label; cannot move without overwrite -> conflict
                raise RuntimeError("slot_occupied_conflict")
            # Otherwise, overwriting occupant is not allowed
            raise RuntimeError("slot_occupied_conflict")

        # Slot empty. Does same label already exist under parent?
        existing = conn.execute("SELECT id, slot FROM nodes WHERE parent_id=? AND label=?", (parent_id, label)).fetchone()
        if existing:
            # Move existing label to requested slot
            # Ensure UNIQUE(parent_id, slot) by updating directly; will raise on race
            conn.execute("UPDATE nodes SET slot=? WHERE id=?", (slot, existing["id"]))
            return {"action": "moved", "node_id": int(existing["id"]), "parent_id": parent_id, "slot": slot, "label": label}

        # Create fresh child at requested slot
        cur = conn.execute(
            "INSERT INTO nodes (parent_id, label, depth, slot) VALUES (?,?,?,?)",
            (parent_id, label, new_depth, slot)
        )
        node_id = cur.lastrowid
        return {"action": "created", "node_id": int(node_id), "parent_id": parent_id, "slot": slot, "label": label}


def detect_conflicts(conn: sqlite3.Connection, limit: int, offset: int, q: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns parents with potential issues:
      - overfilled (>5 children) OR slot conflicts OR null-slot kids
      - underfilled (<5)
      - duplicate parent nodes with same (parent_id,label) (legacy)
    """
    params = []
    where = ""
    if q:
        where = "WHERE LOWER(p.label) LIKE ?"
        params.append(f"%{q.lower()}%")

    sql = f"""
    WITH kids AS (
      SELECT p.id AS parent_id, p.label, p.depth,
             COUNT(c.id) AS child_count,
             SUM(CASE WHEN c.slot IS NULL THEN 1 ELSE 0 END) AS null_slots
      FROM nodes p
      LEFT JOIN nodes c ON c.parent_id = p.id
      {where}
      GROUP BY p.id
    ), slot_dups AS (
      SELECT parent_id, COUNT(*) AS dup_slots
      FROM (
        SELECT parent_id, slot, COUNT(*) AS cnt
        FROM nodes
        WHERE slot IS NOT NULL
        GROUP BY parent_id, slot
        HAVING COUNT(*) > 1
      )
    ), parent_dups AS (
      SELECT parent_id, label, COUNT(*) AS cnt
      FROM (
        SELECT parent_id, label, COUNT(*) AS c
        FROM nodes
        GROUP BY parent_id, label
        HAVING COUNT(*) > 1
      ) t
    )
    SELECT k.parent_id, k.label, k.depth, k.child_count,
           COALESCE(sd.dup_slots,0) AS slot_dup_count,
           COALESCE(k.null_slots,0) AS null_slot_count,
           CASE WHEN k.child_count > 5 THEN 1 ELSE 0 END AS overfilled,
           CASE WHEN k.child_count < 5 THEN 1 ELSE 0 END AS underfilled,
           COALESCE(pd.cnt,0) AS duplicate_parents
    FROM kids k
    LEFT JOIN slot_dups sd ON sd.parent_id = k.parent_id
    LEFT JOIN parent_dups pd ON pd.parent_id = k.parent_id AND pd.label = k.label
    WHERE (k.child_count > 5 OR k.child_count < 5 OR COALESCE(sd.dup_slots,0) > 0 OR COALESCE(k.null_slots,0) > 0 OR COALESCE(pd.cnt,0) > 1)
    ORDER BY k.depth ASC, k.label ASC
    LIMIT ? OFFSET ?;
    """
    cur = conn.execute(sql, params + [int(limit), int(offset)])
    items = []
    for r in cur.fetchall():
        items.append({
            "parent_id": r["parent_id"], "label": r["label"], "depth": int(r["depth"]),
            "child_count": int(r["child_count"]),
            "slot_dup_count": int(r["slot_dup_count"]),
            "null_slot_count": int(r["null_slot_count"]),
            "overfilled": bool(r["overfilled"]),
            "underfilled": bool(r["underfilled"]),
            "duplicate_parents": int(r["duplicate_parents"])
        })
    total = len(items)  # lightweight; acceptable for MVP
    return {"items": items, "total": total, "limit": int(limit), "offset": int(offset)}


def normalize_parent(conn: sqlite3.Connection, parent_id: int) -> Dict[str, Any]:
    """
    Re-slot children into 1..5, remove null-slot issues, resolve duplicate-slot
    by stable order (label ASC, id ASC). If >5, keep first 5; return 'excess' for manual action.
    """
    ensure_schema(conn)
    with tx(conn):
        cur = conn.execute("SELECT id, label FROM nodes WHERE parent_id=?", (parent_id,))
        children = [{"id": r["id"], "label": r["label"]} for r in cur.fetchall()]
        # stable order by existing slot then id then label
        cur2 = conn.execute("SELECT id, slot, label FROM nodes WHERE parent_id=? ORDER BY (slot IS NULL), slot, id", (parent_id,))
        ordered = [{"id": r["id"], "slot": r["slot"], "label": r["label"]} for r in cur2.fetchall()]
        kept = ordered[:5]
        excess = ordered[5:]
        # assign slots 1..5 to kept sequentially
        for i, ch in enumerate(kept, start=1):
            conn.execute("UPDATE nodes SET slot=? WHERE id=?", (i, ch["id"]))
        # do not delete excess automatically; report back
        return {
            "kept": [{"id": c["id"], "slot": i+1 if i < 5 else 5, "label": c["label"]} for i, c in enumerate(kept)],
            "excess_children": [{"id": c["id"], "slot": c["slot"], "label": c["label"]} for c in excess]
        }


def merge_duplicate_parents(conn: sqlite3.Connection, parent_id: int, label: str, keep_id: int) -> Dict[str, Any]:
    """
    Merge duplicate parent nodes under the same parent (legacy data).
    For all nodes X with same parent_id and label, move their children to keep_id (re-slot later),
    then delete X (except keep_id). Finally, call normalize_parent(keep_id).
    """
    ensure_schema(conn)
    moved = 0
    deleted = 0
    with tx(conn):
        cur = conn.execute("SELECT id FROM nodes WHERE parent_id=? AND label=?", (parent_id, label))
        ids = [r["id"] for r in cur.fetchall()]
        for nid in ids:
            if nid == keep_id:
                continue
            # move children of nid -> keep_id
            conn.execute("UPDATE nodes SET parent_id=? WHERE parent_id=?", (keep_id, nid))
            # outcomes move: none (only leaves), they stay on same leaf ids
            conn.execute("DELETE FROM nodes WHERE id=?", (nid,))
            deleted += 1
        moved = deleted  # proxy
        norm = normalize_parent(conn, keep_id)
    return {"moved_from_duplicates": moved, "deleted_duplicates": deleted, "normalized": norm}


def root_options(conn: sqlite3.Connection) -> List[str]:
    cur = conn.execute("SELECT DISTINCT label FROM nodes WHERE depth=0 ORDER BY label")
    return [r["label"] for r in cur.fetchall()]


def _node_id_by_path(conn: sqlite3.Connection, path: List[str]) -> Optional[int]:
    if not path:
        return None
    # root
    cur = conn.execute("SELECT id FROM nodes WHERE depth=0 AND label=?", (path[0],))
    row = cur.fetchone()
    if not row:
        return None
    nid = row["id"]
    # traverse Node 1..5 by label
    for depth, label in enumerate(path[1:], start=1):
        if not label:
            break
        cur = conn.execute("SELECT id FROM nodes WHERE parent_id=? AND label=? AND depth=?", (nid, label, depth))
        row = cur.fetchone()
        if not row:
            return None
        nid = row["id"]
    return nid


def navigate_path(conn: sqlite3.Connection, path: List[str]) -> Dict[str, Any]:
    """
    Given path [root, n1, n2, ...], return next options and outcome if any at current node.
    """
    nid = _node_id_by_path(conn, path)
    if nid is None:
        return {"node_id": None, "options": [], "outcome": None}
    # children
    cur = conn.execute("SELECT slot, label FROM nodes WHERE parent_id=? ORDER BY slot", (nid,))
    options = [{"slot": r["slot"], "label": r["label"]} for r in cur.fetchall() if r["slot"] is not None]
    # outcome at current node?
    o = conn.execute("SELECT diagnostic_triage, actions FROM outcomes WHERE node_id=?", (nid,)).fetchone()
    outcome = None
    if o:
        outcome = {"diagnostic_triage": o["diagnostic_triage"], "actions": o["actions"]}
    return {"node_id": int(nid), "options": options, "outcome": outcome}


def get_conflict_group(conn: sqlite3.Connection, parent_id: int, label: str) -> Dict[str, Any]:
    """
    A 'conflict group' = all nodes N such that N.parent_id = parent_id AND N.label = label.
    Returns:
      { group: [{id}], children: [{child_id, from_id, slot, label}], summary:{unique_children:int, total_children:int} }
    If there is only one node in the group, we still return its children to allow normalization.
    """
    ensure_schema(conn)
    group_ids = [r["id"] for r in conn.execute(
        "SELECT id FROM nodes WHERE parent_id=? AND label=? ORDER BY id", (parent_id, label)
    ).fetchall()]
    children: List[Dict[str, Any]] = []
    for gid in group_ids:
        cur = conn.execute("SELECT id, slot, label FROM nodes WHERE parent_id=? ORDER BY (slot IS NULL), slot, id", (gid,))
        for r in cur.fetchall():
            children.append({"child_id": r["id"], "from_id": gid, "slot": r["slot"], "label": r["label"]})
    unique_children = len({c["label"] for c in children})
    return {
        "group": [{"id": gid} for gid in group_ids],
        "children": children,
        "summary": {"unique_children": unique_children, "total_children": len(children)}
    }


def resolve_conflict_group(conn: sqlite3.Connection, parent_id: int, label: str, keep_id: int, chosen_labels: List[str]) -> Dict[str, Any]:
    """
    Transactionally:
      1) Validate chosen_labels: exactly 5 unique non-empty.
      2) Merge all duplicates into keep_id:
         - Move children to keep_id (re-parent).
         - Delete duplicate parents (except keep_id).
      3) Under keep_id, replace children with the 5 chosen labels in slots 1..5:
         - If a child with the chosen label exists elsewhere under keep_id, update its slot.
         - Else create it.
         - Delete any other children under keep_id not in chosen set.
    """
    ensure_schema(conn)
    chosen = ensure_unique_5(chosen_labels)

    with tx(conn):
        # Collect duplicates
        ids = [r["id"] for r in conn.execute(
            "SELECT id FROM nodes WHERE parent_id=? AND label=?", (parent_id, label)
        ).fetchall()]
        if keep_id not in ids:
            raise LookupError("keep_id_not_in_group")

        # Move children of other duplicates to keep_id, then delete dup parents
        moved = 0
        for nid in ids:
            if nid == keep_id:
                continue
            conn.execute("UPDATE nodes SET parent_id=? WHERE parent_id=?", (keep_id, nid))
            conn.execute("DELETE FROM nodes WHERE id=?", (nid,))
            moved += 1

        # Current children under keep_id
        cur = conn.execute("SELECT id, label FROM nodes WHERE parent_id=?", (keep_id,))
        existing = {r["label"]: r["id"] for r in cur.fetchall()}

        # Ensure slots 1..5 exactly chosen
        # Delete anything not chosen
        for lab, cid in list(existing.items()):
            if lab not in chosen:
                conn.execute("DELETE FROM nodes WHERE id=?", (cid,))
                existing.pop(lab, None)

        # Upsert/move for chosen labels in order
        for i, lab in enumerate(chosen, start=1):
            if lab in existing:
                conn.execute("UPDATE nodes SET slot=?, depth=(SELECT depth+1 FROM nodes WHERE id=?) WHERE id=?", (i, keep_id, existing[lab]))
            else:
                # create
                parent_depth = conn.execute("SELECT depth FROM nodes WHERE id=?", (keep_id,)).fetchone()[0]
                new_depth = int(parent_depth) + 1
                conn.execute("INSERT INTO nodes(parent_id, label, depth, slot) VALUES (?,?,?,?)", (keep_id, lab, new_depth, i))

    return {"ok": True, "moved_duplicates": moved, "kept": keep_id, "chosen": chosen}


def list_parent_labels(conn: sqlite3.Connection, limit: int, offset: int,
                       incomplete_only: bool = True,
                       depth: Optional[int] = None,
                       q: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns unique parent labels with occurrence counts and how many are incomplete.
    """
    ensure_schema(conn)
    where = ["p.label IS NOT NULL", "TRIM(p.label) <> ''", "LOWER(p.label) <> 'nan'"]
    params: List[Any] = []
    if depth is not None:
        where.append("p.depth = ?")
        params.append(int(depth))
    if q:
        where.append("LOWER(p.label) LIKE ?")
        params.append(f"%{q.lower()}%")
    where_sql = "WHERE " + " AND ".join(where)

    sql = f"""
    WITH kids AS (
      SELECT p.id, p.label, p.depth, COUNT(c.id) AS child_count
      FROM nodes p
      LEFT JOIN nodes c ON c.parent_id = p.id
      {where_sql}
      GROUP BY p.id
    ),
    agg AS (
      SELECT label,
             COUNT(*) AS occurrences,
             SUM(CASE WHEN child_count < 5 THEN 1 ELSE 0 END) AS incomplete_count,
             MIN(depth) AS min_depth,
             MAX(depth) AS max_depth
      FROM kids
      GROUP BY label
    )
    SELECT label, occurrences, incomplete_count, min_depth, max_depth
    FROM agg
    {"WHERE incomplete_count > 0" if incomplete_only else ""}
    ORDER BY label ASC
    LIMIT ? OFFSET ?;
    """
    cur = conn.execute(sql, params + [int(limit), int(offset)])
    items = [{
        "label": r["label"],
        "occurrences": int(r["occurrences"]),
        "incomplete_count": int(r["incomplete_count"] or 0),
        "min_depth": int(r["min_depth"]),
        "max_depth": int(r["max_depth"]),
    } for r in cur.fetchall()]
    # NOTE: total = count of labels after filter; for full paging implement COUNT(*) over agg
    return {"items": items, "total": len(items), "limit": int(limit), "offset": int(offset)}


def aggregate_children_for_label(conn: sqlite3.Connection, label: str) -> Dict[str, Any]:
    """
    For all parents with the given label, return:
      - union of children labels with frequencies
      - by_parent detail (parent_id -> its children)
    """
    ensure_schema(conn)
    parent_ids = [r["id"] for r in conn.execute("SELECT id FROM nodes WHERE label=?", (label,)).fetchall()]
    by_parent = []
    freq = {}
    for pid in parent_ids:
        cur = conn.execute("SELECT id, slot, label FROM nodes WHERE parent_id=? ORDER BY slot", (pid,))
        kids = []
        for rr in cur.fetchall():
            lab = sanitize_label(rr["label"])
            if lab is None:  # hide blanks from the union and detail
                continue
            kids.append({"id": rr["id"], "slot": rr["slot"], "label": lab})
            freq[lab] = freq.get(lab, 0) + 1
        by_parent.append({"parent_id": pid, "children": kids})
    union = [{"label": k, "freq": v} for k, v in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))]
    return {"label": label, "occurrences": len(parent_ids), "union": union, "by_parent": by_parent}


def apply_default_children_for_label(conn: sqlite3.Connection, label: str, chosen: List[str]) -> Dict[str, Any]:
    """
    For every parent node with this label:
      - replace children with exactly the chosen 5 labels, slots 1..5 (create/move/delete)
      - depth = parent.depth + 1
    """
    ensure_schema(conn)
    chosen = ensure_unique_5(chosen)
    updated = 0
    created = 0
    deleted = 0
    moved = 0
    with tx(conn):
        cur = conn.execute("SELECT id, depth FROM nodes WHERE label=?", (label,))
        parents = [{"id": r["id"], "depth": int(r["depth"])} for r in cur.fetchall()]
        for p in parents:
            pid, base_depth = p["id"], p["depth"]
            # free slots first to avoid unique collisions
            conn.execute("UPDATE nodes SET slot = NULL WHERE parent_id=?", (pid,))
            # fetch after freeing
            ex_cur = conn.execute("SELECT id, label FROM nodes WHERE parent_id=?", (pid,))
            existing = {r["label"]: r["id"] for r in ex_cur.fetchall() if r["label"]}
            # delete non chosen
            for lab, cid in list(existing.items()):
                if lab not in chosen:
                    conn.execute("DELETE FROM nodes WHERE id=?", (cid,))
                    deleted += 1
                    existing.pop(lab, None)
            # upsert / move to exact slots
            for i, lab in enumerate(chosen, start=1):
                if lab in existing:
                    # Don't update depth if it would exceed the constraint
                    new_depth = min(base_depth + 1, 5)
                    conn.execute("UPDATE nodes SET slot=?, depth=? WHERE id=?", (i, new_depth, existing[lab]))
                    moved += 1
                else:
                    # Don't create children if parent is already at max depth
                    if base_depth < 5:
                        new_depth = min(base_depth + 1, 5)
                        conn.execute(
                            "INSERT INTO nodes(parent_id,label,depth,slot) VALUES (?,?,?,?)",
                            (pid, lab, new_depth, i)
                        )
                        created += 1
            updated += 1
    return {"ok": True, "label": label, "parents_updated": updated, "children_created": created, "children_deleted": deleted, "children_moved": moved}
