"""
Benchmark SQLite performance on realistic Lorien dataset for key queries.

Seeds a 5-ary tree up to depth 5 across multiple roots, then measures:
- List roots (depth=0)
- Case-insensitive label lookup (root and contextual child)

Runs timings before and after creating perf indexes.
"""

import sqlite3
import sys
import time
from pathlib import Path

# Ensure repo root is on sys.path for api imports
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

ROOTS = 10  # number of roots to generate
BRANCH = 5  # branching factor per level
DEPTH = 5  # maximum depth (children levels)


def apply_migrations(db_path: str):
    """Apply SQL migrations directly without importing FastAPI modules."""
    mig_dir = ROOT / "api" / "db" / "migrations"
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute("PRAGMA foreign_keys=ON;")
        for path in sorted(mig_dir.glob("*.sql")):
            sql = path.read_text(encoding="utf-8").strip()
            if sql:
                conn.executescript(sql)
        conn.commit()
    finally:
        conn.close()


def seed_data(conn: sqlite3.Connection):
    cur = conn.cursor()
    conn.execute("BEGIN")
    try:
        root_ids = []
        for r in range(1, ROOTS + 1):
            label = f"VM {r}"
            cur.execute(
                "INSERT INTO nodes(parent_id, depth, slot, label, is_leaf) VALUES (NULL, 0, NULL, ?, 0)",
                (label,),
            )
            root_id = cur.lastrowid
            root_ids.append(root_id)

            # BFS generate levels 1..DEPTH
            level_nodes = [root_id]
            for d in range(1, DEPTH + 1):
                next_level = []
                for parent in level_nodes:
                    for slot in range(1, BRANCH + 1):
                        nlabel = f"R{r}-D{d}-S{slot}"
                        cur.execute(
                            "INSERT INTO nodes(parent_id, depth, slot, label, is_leaf) VALUES (?,?,?,?,?)",
                            (parent, d, slot, nlabel, 1 if d == DEPTH else 0),
                        )
                        next_level.append(cur.lastrowid)
                level_nodes = next_level
        conn.commit()
        return root_ids
    except Exception:
        conn.rollback()
        raise


def drop_perf_indexes(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("DROP INDEX IF EXISTS idx_nodes_depth")
    cur.execute("DROP INDEX IF EXISTS idx_nodes_label_norm")
    conn.commit()


def create_perf_indexes(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_depth ON nodes(depth)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_nodes_label_norm ON nodes( lower(trim(label)) )")
    conn.commit()
    try:
        conn.execute("ANALYZE")
    except Exception:
        pass


def bench(cur: sqlite3.Cursor, root_ids: list[int]):
    reps = 50
    results = {}

    # 1) List roots
    t0 = time.perf_counter()
    for _ in range(reps):
        rows = cur.execute("SELECT id,label FROM nodes WHERE depth=0 ORDER BY id").fetchall()
        assert len(rows) == ROOTS
    results["list_roots_ms"] = (time.perf_counter() - t0) * 1000 / reps

    # 2) Root lookup by normalized label
    target_root_label = f"vm {ROOTS}"  # lowercase to force normalization
    t0 = time.perf_counter()
    for _ in range(reps):
        row = cur.execute(
            "SELECT id FROM nodes WHERE depth=0 AND lower(trim(label))=?", (target_root_label,)
        ).fetchone()
        assert row is not None
    results["root_label_norm_ms"] = (time.perf_counter() - t0) * 1000 / reps

    # 3) Contextual child lookup by normalized label (pick a mid-depth parent)
    # Choose root 1, depth 2 parent (slot 3 under depth 1 slot 2)
    parent = cur.execute(
        (
            """
            SELECT id FROM nodes WHERE parent_id = (
                SELECT id FROM nodes WHERE parent_id = (
                    SELECT id FROM nodes WHERE depth=0 AND label=?
                ) AND depth=1 AND slot=2
            ) AND depth=2 AND slot=3
            """
        ),
        ("VM 1",),
    ).fetchone()[0]
    target_child_label = "r1-d3-s4"  # lowercase normalized target under that lineage
    t0 = time.perf_counter()
    for _ in range(reps):
        row = cur.execute(
            "SELECT id FROM nodes WHERE parent_id=? AND depth=? AND lower(trim(label))=?",
            (parent, 3, target_child_label),
        ).fetchone()
        assert row is not None
    results["child_label_norm_ms"] = (time.perf_counter() - t0) * 1000 / reps

    return results


def main():
    bench_dir = Path(".bench")
    bench_dir.mkdir(exist_ok=True)
    db_path = bench_dir / "perf.db"
    if db_path.exists():
        db_path.unlink()

    apply_migrations(str(db_path))
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        roots = seed_data(conn)
        cur = conn.cursor()

        # Before perf indexes (drop if present)
        drop_perf_indexes(conn)
        before = bench(cur, roots)

        # After perf indexes
        create_perf_indexes(conn)
        after = bench(cur, roots)

        print(f"Benchmark results (avg ms per op, {ROOTS} roots, 5^{DEPTH} tree):")
        for k in sorted(before.keys()):
            print(
                f"- {k}: before={before[k]:.3f} ms, after={after[k]:.3f} ms, delta={(before[k] - after[k]):.3f} ms"
            )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
