"""
Conflicts detection engine for variant 5-sets.
Detects duplicate parents (same depth, norm(label)) with different 5-child sets.
"""

import unicodedata
from collections import defaultdict


def _norm(s: str) -> str:
    """Normalize string for grouping/lookup (NFKC + casefold + whitespace collapse)"""
    if not s: 
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = " ".join(s.strip().split())
    return s.casefold()


def _sig(labels):
    """Create signature from normalized labels (sorted, unique)"""
    return "|".join(sorted({_norm(x) for x in labels if _norm(x)}))


def compute_variant_conflicts(parents, children):
    """
    Detect conflicts: duplicate parents with variant 5-sets.
    
    Args:
        parents: [{id, depth, label}] - parent nodes
        children: [{parent_id, label}] - child nodes
        
    Returns:
        List of conflict items for groups (depth, norm(label)) that contain parents,
        each with exactly 5 direct children, and ≥2 distinct signature sets.
    """
    # 1) Direct children per parent
    kids = defaultdict(list)
    for c in children:
        kids[c["parent_id"]].append(c["label"])

    # 2) Filter parents to those with exactly 5 unique normalized child labels
    exact5 = {}
    for p in parents:
        pid = p["id"]
        labs = kids.get(pid, [])
        sig = _sig(labs)
        if len([x for x in sig.split("|") if x]) == 5:
            exact5[pid] = sig

    # 3) Group parents by (depth, norm(parent_label))
    grp = defaultdict(list)
    meta = {}
    for p in parents:
        pid = p["id"]
        meta[pid] = p
        if pid in exact5:
            key = (p["depth"], _norm(p["label"]))
            grp[key].append(pid)

    # 4) Keep groups with ≥2 distinct signatures
    items = []
    for key, ids in grp.items():
        sigs = {exact5[i] for i in ids}
        if len(sigs) >= 2:
            depth, _ = key
            # Choose a stable display label (raw) from the smallest parent id
            rep = min(ids)
            display = meta[rep]["label"]  # raw
            items.append({
                "parent_id": rep,
                "label": display,
                "depth": depth,
                "child_count": 5,
                "duplicate_parents": len(ids),
                "variant_sets": len(sigs),
                "group_parent_ids": ids,
            })
    return items