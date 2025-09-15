"""
Conflicts service using the new conflicts engine.
"""

from api.core.conflicts_engine import compute_variant_conflicts
from api.repositories.tree_repo import list_candidate_parents, list_direct_children_for_parents


def list_conflicts(limit: int = 50, offset: int = 0):
    """List conflicts: duplicate parents with variant 5-sets"""
    parents = list_candidate_parents(limit, offset)
    children = list_direct_children_for_parents([p["id"] for p in parents])
    items = compute_variant_conflicts(parents, children)
    
    # Ensure ints are non-null + shape
    for it in items:
        it["child_count"] = int(it.get("child_count") or 0)
        it["duplicate_parents"] = int(it.get("duplicate_parents") or 0)
        it["variant_sets"] = int(it.get("variant_sets") or 0)
    
    return {"items": items, "total": len(items), "limit": limit, "offset": offset}


def load_group(node_id: int):
    """
    Given a parent id, return the group of all parents with same (depth, norm(label)) 
    and union of their direct children.
    """
    import sqlite3
    import unicodedata
    from api.settings import get_db_path

    def _norm(s):
        if not s: 
            return ""
        s = unicodedata.normalize("NFKC", s)
        s = " ".join(s.strip().split())
        return s.casefold()

    conn = sqlite3.connect(get_db_path())
    cur = conn.execute("SELECT label, depth FROM nodes WHERE id=?", (node_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return {"group": [], "children": [], "summary": {"unique_children": 0, "total_children": 0}}
    
    label_raw, depth = row
    key_norm = _norm(label_raw)

    # Find all parent ids with same (depth, norm(label))
    cur = conn.execute("SELECT id, label FROM nodes WHERE depth=? AND parent_id IS NOT NULL", (depth,))
    group_ids = []
    label_display = None
    for pid, lbl in cur.fetchall():
        if _norm(lbl) == key_norm:
            group_ids.append(pid)
            if label_display is None:
                label_display = lbl

    # Union of their direct children
    q = ",".join(["?"] * len(group_ids)) if group_ids else None
    children = []
    if q:
        cur = conn.execute(f"""
          SELECT id, parent_id, slot, label
          FROM nodes
          WHERE parent_id IN ({q})
          ORDER BY parent_id, slot NULLS LAST, id
        """, group_ids)
        children = [{"child_id": r[0], "from_id": r[1], "slot": r[2], "label": r[3]} for r in cur.fetchall()]
    
    conn.close()
    return {
        "group": [{"id": gid, "label": label_display, "depth": depth} for gid in group_ids],
        "children": children,
        "summary": {
            "unique_children": len(set((c["from_id"], c["label"]) for c in children)),
            "total_children": len(children)
        }
    }