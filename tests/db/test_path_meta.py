import sqlite3
import tempfile
import pytest
from api.db.migrate import apply_migrations
from Engines.EngineLongBow.store import _upsert_path_meta, _get_or_create_node

def test_path_meta_upsert_behavior():
    """Test that path_meta upsert works correctly with COALESCE update logic."""
    # Create a temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        # Apply migrations to create schema including path_meta table
        apply_migrations(db_path)
        
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys=ON")
        
        try:
            conn.execute("BEGIN")
            
            # Create a simple path: Root -> Child
            root_id = _get_or_create_node(conn, None, 0, "TestRoot")
            child_id = _get_or_create_node(conn, root_id, 1, "TestChild")
            
            # First upsert: set both d6 and notes
            _upsert_path_meta(conn, child_id, "TRIAGE_1", "ACTION_1")
            
            # Verify initial insert
            cur = conn.execute("SELECT d6, notes FROM path_meta WHERE leaf_id = ?", (child_id,))
            row = cur.fetchone()
            assert row is not None
            assert row[0] == "TRIAGE_1"
            assert row[1] == "ACTION_1"
            
            # Second upsert: update only d6, notes should remain
            _upsert_path_meta(conn, child_id, "TRIAGE_2", None)
            
            # Verify COALESCE update: d6 updated, notes preserved
            cur = conn.execute("SELECT d6, notes FROM path_meta WHERE leaf_id = ?", (child_id,))
            row = cur.fetchone()
            assert row is not None
            assert row[0] == "TRIAGE_2"  # Updated
            assert row[1] == "ACTION_1"  # Preserved
            
            # Third upsert: update only notes, d6 should remain
            _upsert_path_meta(conn, child_id, None, "ACTION_2")
            
            # Verify COALESCE update: notes updated, d6 preserved
            cur = conn.execute("SELECT d6, notes FROM path_meta WHERE leaf_id = ?", (child_id,))
            row = cur.fetchone()
            assert row is not None
            assert row[0] == "TRIAGE_2"  # Preserved
            assert row[1] == "ACTION_2"  # Updated
            
            # Verify only one row exists (upsert behavior)
            cur = conn.execute("SELECT COUNT(*) FROM path_meta WHERE leaf_id = ?", (child_id,))
            count = cur.fetchone()[0]
            assert count == 1, f"Expected 1 row, found {count}"
            
            conn.commit()
            
        finally:
            conn.close()
            
    finally:
        # Clean up temporary file
        import os
        os.unlink(db_path)


def test_path_meta_cascade_delete():
    """Test that deleting a node cascades to path_meta."""
    # Create a temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    try:
        # Apply migrations to create schema including path_meta table
        apply_migrations(db_path)
        
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys=ON")
        
        try:
            conn.execute("BEGIN")
            
            # Create a simple path: Root -> Child
            root_id = _get_or_create_node(conn, None, 0, "TestRoot")
            child_id = _get_or_create_node(conn, root_id, 1, "TestChild")
            
            # Add metadata
            _upsert_path_meta(conn, child_id, "TRIAGE_1", "ACTION_1")
            
            # Verify metadata exists
            cur = conn.execute("SELECT COUNT(*) FROM path_meta WHERE leaf_id = ?", (child_id,))
            count = cur.fetchone()[0]
            assert count == 1
            
            # Delete the child node
            conn.execute("DELETE FROM nodes WHERE id = ?", (child_id,))
            
            # Verify metadata was cascaded away
            cur = conn.execute("SELECT COUNT(*) FROM path_meta WHERE leaf_id = ?", (child_id,))
            count = cur.fetchone()[0]
            assert count == 0, f"Expected 0 rows after cascade delete, found {count}"
            
            conn.commit()
            
        finally:
            conn.close()
            
    finally:
        # Clean up temporary file
        import os
        os.unlink(db_path)
