from __future__ import annotations
import sqlite3

def upsert_triage(conn: sqlite3.Connection, node_id: int, diagnostic_triage: str, actions: str):
    """
    Upsert triage data for a leaf node (depth == 5).
    
    Args:
        conn: Database connection
        node_id: ID of the node to update
        diagnostic_triage: Diagnostic triage text
        actions: Actions text
        
    Raises:
        ValueError: If node not found or not a leaf node
    """
    # Enforce leaf-only: depth == 5
    d = conn.execute("SELECT depth FROM nodes WHERE id=?", (node_id,)).fetchone()
    if not d:
        raise ValueError("node not found")
    if d[0] != 5:
        raise ValueError("triage allowed only for leaf nodes (depth=5)")
    
    # Upsert
    conn.execute("""
        INSERT INTO triage(node_id, diagnostic_triage, actions)
        VALUES(?,?,?)
        ON CONFLICT(node_id) DO UPDATE SET 
            diagnostic_triage=excluded.diagnostic_triage, 
            actions=excluded.actions
    """, (node_id, diagnostic_triage, actions))
    conn.commit()
