from typing import Dict, Any
import sqlite3

from api.db import get_conn, ensure_schema, tx

CLEARABLE_OPTIONAL_TABLES = ["triage", "flags"]  # if present
DICTIONARY_TABLES = ["dictionary_terms"]         # cleared only when include_dictionary=True

def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    cur = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (name,))
    return cur.fetchone() is not None

def _count_table(conn: sqlite3.Connection, name: str) -> int:
    try:
        return int(conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0])
    except Exception:
        return 0

def clear_workspace(conn: sqlite3.Connection, include_dictionary: bool = False) -> Dict[str, Any]:
    """
    Transactionally clear workspace content:
      - Deletes nodes (cascades to outcomes)
      - Deletes optional tables if present: triage, flags
      - Optionally clears dictionary tables
      - Runs PRAGMA integrity_check afterwards
    Returns a summary with counts after clearing.
    """
    ensure_schema(conn)

    with tx(conn):
        # Delete dependent/optional tables first (defensive; CASCADE handles outcomes when nodes deleted)
        for tbl in CLEARABLE_OPTIONAL_TABLES:
            if _table_exists(conn, tbl):
                conn.execute(f"DELETE FROM {tbl}")

        # Nodes (cascades to outcomes)
        if _table_exists(conn, "nodes"):
            conn.execute("DELETE FROM nodes")

        # Dictionary — only if requested
        dict_cleared = False
        if include_dictionary:
            for tbl in DICTIONARY_TABLES:
                if _table_exists(conn, tbl):
                    conn.execute(f"DELETE FROM {tbl}")
                    dict_cleared = True

    # Integrity check
    chk = conn.execute("PRAGMA integrity_check").fetchone()
    ok = (chk and str(chk[0]).lower() == "ok")

    if not ok:
        # Fail loudly if DB isn't consistent after transactional clear
        raise RuntimeError("SQLite integrity_check failed after clear")

    # Post-clear counts (should be zeros/near-zero)
    summary = {
        "nodes": _count_table(conn, "nodes"),
        "outcomes": _count_table(conn, "outcomes"),
    }
    for tbl in CLEARABLE_OPTIONAL_TABLES:
        if _table_exists(conn, tbl):
            summary[tbl] = _count_table(conn, tbl)
    for tbl in DICTIONARY_TABLES:
        if _table_exists(conn, tbl):
            summary[tbl] = _count_table(conn, tbl)

    return {"ok": True, "dictionary_cleared": dict_cleared, "summary": summary}
