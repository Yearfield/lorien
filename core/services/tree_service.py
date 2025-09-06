"""
Tree service for Edit Tree functionality with optimistic concurrency.
"""

import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from ..models import Node
from storage.sqlite import SQLiteRepository


ETAG_FMT = 'W/"parent-{id}:v{v}"'


def parse_if_match(value: str | None) -> int | None:
    """Parse If-Match header value to extract version."""
    if not value:
        return None
    # Accept W/"parent-123:v7" strictly
    m = re.fullmatch(r'W/\"parent-(\d+):v(\d+)\"', value)
    if not m:
        return None
    return int(m.group(2))


def ensure_parent_version_row(repo: SQLiteRepository, parent_id: int) -> int:
    """Ensure a version row exists for parent and return current version."""
    with repo._get_connection() as conn:
        cursor = conn.cursor()

        # Check if version row exists
        cursor.execute("SELECT version FROM tree_parent_version WHERE parent_id = ?", (parent_id,))
        row = cursor.fetchone()

        if row:
            return row[0]

        # Create default version row
        cursor.execute("""
            INSERT INTO tree_parent_version (parent_id, version, updated_at)
            VALUES (?, 0, ?)
        """, (parent_id, datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")))

        conn.commit()
        return 0


def children_snapshot(repo: SQLiteRepository, parent_id: int) -> Dict[str, Any] | None:
    """Get current snapshot of parent children with version."""
    with repo._get_connection() as conn:
        cursor = conn.cursor()

        # Get parent info
        cursor.execute("SELECT id, label, depth FROM nodes WHERE id = ?", (parent_id,))
        parent_row = cursor.fetchone()
        if not parent_row:
            return None

        parent_id, parent_label, parent_depth = parent_row

        # Get current version
        version = ensure_parent_version_row(repo, parent_id)

        # Get all children (exactly 5 slots)
        children = []
        for slot in range(1, 6):
            cursor.execute("""
                SELECT id, label, updated_at
                FROM nodes
                WHERE parent_id = ? AND slot = ?
            """, (parent_id, slot))

            child_row = cursor.fetchone()
            if child_row:
                node_id, label, updated_at = child_row
                children.append({
                    "slot": slot,
                    "node_id": node_id,
                    "label": label or "",
                    "updated_at": updated_at
                })
            else:
                # Create missing child node
                cursor.execute("""
                    INSERT INTO nodes (parent_id, slot, label, depth, updated_at)
                    VALUES (?, ?, '', ?, ?)
                """, (parent_id, slot, parent_depth + 1,
                     datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")))

                node_id = cursor.lastrowid
                updated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                children.append({
                    "slot": slot,
                    "node_id": node_id,
                    "label": "",
                    "updated_at": updated_at
                })

        conn.commit()

        return {
            "version": version,
            "children": children
        }


def validate_five_slots(children: List) -> None:
    """Validate exactly 5 children with slots 1-5."""
    if len(children) != 5:
        # Handle both dict and Pydantic model cases
        if hasattr(children[0], 'slot'):
            # Pydantic model case
            slots_present = [c.slot for c in children]
        else:
            # Dict case
            slots_present = [c["slot"] for c in children]

        raise ValueError({
            "missing_slots": [s for s in [1,2,3,4,5] if s not in slots_present]
        })

    # Handle both dict and Pydantic model cases
    if hasattr(children[0], 'slot'):
        # Pydantic model case
        slots = sorted(c.slot for c in children)
    else:
        # Dict case
        slots = sorted(c["slot"] for c in children)

    expected = [1, 2, 3, 4, 5]
    if slots != expected:
        missing = [s for s in expected if s not in slots]
        if missing:
            raise ValueError({"missing_slots": missing})


def validate_duplicate_labels(repo: SQLiteRepository, parent_id: int, children: List) -> List[Dict[str, Any]]:
    """Validate no duplicate labels under same parent (case-insensitive)."""
    errors = []

    # Check within submitted children
    labels_seen = {}
    for child in children:
        # Handle both dict and Pydantic model cases
        if hasattr(child, 'label'):
            # Pydantic model case
            label = child.label.strip().lower()
            slot = child.slot
        else:
            # Dict case
            label = child["label"].strip().lower()
            slot = child["slot"]

        if label and label in labels_seen:
            errors.append({
                "loc": ["body", "children", slot - 1, "label"],
                "msg": "Duplicate label under same parent",
                "type": "value_error.duplicate_child_label",
                "ctx": {"slot": slot}
            })
        elif label:
            labels_seen[label] = slot

    # Check against existing siblings in database
    with repo._get_connection() as conn:
        cursor = conn.cursor()

        for child in children:
            # Handle both dict and Pydantic model cases
            if hasattr(child, 'label'):
                # Pydantic model case
                label = child.label.strip()
                slot = child.slot
            else:
                # Dict case
                label = child["label"].strip()
                slot = child["slot"]

            if not label:
                continue

            # Check for conflicts with other children under same parent
            cursor.execute("""
                SELECT slot FROM nodes
                WHERE parent_id = ? AND lower(label) = ? AND slot != ? AND label != ''
            """, (parent_id, label.lower(), slot))

            conflict = cursor.fetchone()
            if conflict:
                errors.append({
                    "loc": ["body", "children", slot - 1, "label"],
                    "msg": "Label conflicts with existing child",
                    "type": "value_error.duplicate_child_label",
                    "ctx": {"slot": slot, "conflicting_slot": conflict[0]}
                })

    return errors


def build_slot_conflicts(submitted: List[Dict[str, Any]], current: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Build conflict details for stale version."""
    conflicts = []

    # Create lookup by slot
    current_by_slot = {c["slot"]: c for c in current["children"]}

    for submitted_child in submitted:
        slot = submitted_child["slot"]
        submitted_label = submitted_child["label"].strip()

        if slot in current_by_slot:
            current_child = current_by_slot[slot]
            current_label = current_child["label"].strip()

            if submitted_label != current_label:
                conflicts.append({
                    "loc": ["body", "children", slot - 1, "label"],
                    "msg": "Slot changed on server",
                    "type": "conflict.slot",
                    "ctx": {
                        "slot": slot,
                        "server_label": current_label,
                        "server_version": current["version"],
                        "client_version": None,  # Will be filled by caller
                        "server_updated_at": current_child["updated_at"]
                    }
                })

    return conflicts


def children_update_apply(repo: SQLiteRepository, parent_id: int, children: List[Dict[str, Any]], current_version: int) -> Dict[str, Any]:
    """Apply children updates atomically."""
    with repo._get_connection() as conn:
        cursor = conn.cursor()

        updated_slots = []
        missing_slots = []

        # Update each child
        for child in children:
            slot = child["slot"]
            new_label = child["label"].strip()

            # Get current child
            cursor.execute("""
                SELECT id, label FROM nodes
                WHERE parent_id = ? AND slot = ?
            """, (parent_id, slot))

            current_row = cursor.fetchone()
            if current_row:
                node_id, current_label = current_row

                # Only update if label changed
                if new_label != current_label:
                    cursor.execute("""
                        UPDATE nodes
                        SET label = ?, updated_at = ?
                        WHERE id = ?
                    """, (new_label, datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), node_id))
                    updated_slots.append(slot)

            # Track missing slots
            if not new_label:
                missing_slots.append(slot)

        # Get new version after trigger bump
        cursor.execute("SELECT version FROM tree_parent_version WHERE parent_id = ?", (parent_id,))
        new_version = cursor.fetchone()[0]

        conn.commit()

        return {
            "parent_id": parent_id,
            "version": new_version,
            "missing_slots": missing_slots,
            "updated": updated_slots
        }


def children_read(repo: SQLiteRepository, parent_id: int) -> Dict[str, Any] | None:
    """Read parent children with full context."""
    # Get children snapshot
    snapshot = children_snapshot(repo, parent_id)
    if not snapshot:
        return None

    with repo._get_connection() as conn:
        cursor = conn.cursor()

        # Get parent info and build path
        cursor.execute("""
            SELECT n.id, n.label, n.depth
            FROM nodes n
            WHERE n.id = ?
        """, (parent_id,))

        parent_row = cursor.fetchone()
        if not parent_row:
            return None

        parent_id, parent_label, parent_depth = parent_row

        # Build path by walking up from parent
        path_parts = []
        current_id = parent_id

        while current_id:
            cursor.execute("SELECT label, parent_id FROM nodes WHERE id = ?", (current_id,))
            path_row = cursor.fetchone()
            if path_row:
                path_parts.insert(0, path_row[0])
                current_id = path_row[1]
            else:
                break

        # Path structure
        path_data = {
            "node_id": parent_id,
            "is_leaf": False,  # Parents are never leaves
            "depth": parent_depth,
            "vital_measurement": path_parts[0] if path_parts else parent_label,
            "nodes": [""] * 5  # Parents don't have node slots in path
        }

        # Calculate missing slots
        missing_slots = [slot for child in snapshot["children"] if not child["label"] for slot in [child["slot"]]]

        return {
            "parent_id": parent_id,
            "version": snapshot["version"],
            "missing_slots": missing_slots,
            "children": snapshot["children"],
            "path": path_data,
            "etag": ETAG_FMT.format(id=parent_id, v=snapshot["version"])
        }