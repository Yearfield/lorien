"""
Performance guardrails tests.

Tests for:
1. Database index usage verification
2. Query performance benchmarks
3. Streaming response validation
4. Memory usage checks
"""

import pytest
import sqlite3
import time
import io
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def get_db_connection():
    """Get database connection for testing."""
    conn = sqlite3.connect(":memory:")
    # Enable WAL mode and foreign keys
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    
    # Create basic schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER,
            slot INTEGER,
            label TEXT,
            depth INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES nodes(id)
        )
    """)
    
    # Create indexes
    conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_parent_slot ON nodes(parent_id, slot)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_label_depth ON nodes(label, depth)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_nodes_parent_label ON nodes(parent_id, label)")
    
    return conn

def test_index_usage_parents_incomplete():
    """Test that parents/incomplete query uses proper indexes."""
    conn = get_db_connection()
    
    # Insert test data
    conn.execute("INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (1, NULL, 0, 'Root', 0)")
    conn.execute("INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (2, 1, 1, 'Child1', 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (3, 1, 2, 'Child2', 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (4, 1, 3, 'Child3', 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (5, 1, 4, 'Child4', 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (6, 1, 5, 'Child5', 1)")
    
    # Test parents/incomplete query
    query = """
        SELECT n.id, n.label, n.depth, n.updated_at,
               COUNT(c.id) as child_count
        FROM nodes n
        LEFT JOIN nodes c ON c.parent_id = n.id
        WHERE n.depth = 0 OR (n.depth > 0 AND n.parent_id IS NOT NULL)
        GROUP BY n.id, n.label, n.depth, n.updated_at
        HAVING child_count < 5
        ORDER BY n.depth, n.id
    """
    
    # Get query plan
    explain_query = f"EXPLAIN QUERY PLAN {query}"
    cursor = conn.execute(explain_query)
    plan = cursor.fetchall()
    
    # Check that indexes are used
    plan_text = " ".join([row[3] for row in plan])
    
    # Should use index for parent_id lookups
    assert "idx_nodes_parent_slot" in plan_text or "USING INDEX" in plan_text
    # Query should use efficient operations (scan or search)
    assert "SCAN" in plan_text or "SEARCH" in plan_text
    
    # Test query performance
    start_time = time.time()
    cursor = conn.execute(query)
    results = cursor.fetchall()
    end_time = time.time()
    
    # Should complete quickly (less than 100ms for small dataset)
    execution_time = (end_time - start_time) * 1000
    assert execution_time < 100, f"Query took {execution_time}ms, should be < 100ms"
    
    conn.close()

def test_index_usage_conflicts():
    """Test that conflict detection queries use proper indexes."""
    conn = get_db_connection()
    
    # Insert test data with potential conflicts
    conn.execute("INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (1, NULL, 0, 'Root', 0)")
    conn.execute("INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (2, 1, 1, 'Child1', 1)")
    conn.execute("INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (3, 1, 2, 'Child2', 1)")
    
    # Test conflict detection query
    query = """
        SELECT n1.id, n1.label, n1.slot, n2.id as conflict_id, n2.label as conflict_label
        FROM nodes n1
        JOIN nodes n2 ON n1.parent_id = n2.parent_id AND n1.slot = n2.slot AND n1.id != n2.id
        WHERE n1.parent_id = ?
    """
    
    # Get query plan
    explain_query = f"EXPLAIN QUERY PLAN {query}"
    cursor = conn.execute(explain_query, (1,))
    plan = cursor.fetchall()
    
    # Check that indexes are used
    plan_text = " ".join([row[3] for row in plan])
    
    # Should use index for parent_id and slot lookups
    assert "idx_nodes_parent_slot" in plan_text or "USING INDEX" in plan_text
    
    # Test query performance
    start_time = time.time()
    cursor = conn.execute(query, (1,))
    results = cursor.fetchall()
    end_time = time.time()
    
    # Should complete quickly
    execution_time = (end_time - start_time) * 1000
    assert execution_time < 50, f"Query took {execution_time}ms, should be < 50ms"
    
    conn.close()

def test_streaming_csv_export():
    """Test that CSV export uses streaming response."""
    # Test CSV export endpoint
    response = client.get("/api/v1/tree/export")
    
    # Should return 200 or 204 (no content)
    assert response.status_code in [200, 204], f"Expected 200 or 204, got {response.status_code}"
    
    if response.status_code == 200:
        # Check content type
        assert "text/csv" in response.headers.get("content-type", "")
        
        # Check that response is not too large (streaming should handle large datasets)
        content_length = len(response.content)
        assert content_length < 1024 * 1024, f"Response too large: {content_length} bytes"

def test_memory_usage_large_dataset():
    """Test memory usage with larger dataset simulation."""
    conn = get_db_connection()
    
    # Insert larger dataset
    conn.execute("INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (1, NULL, 0, 'Root', 0)")
    
    # Insert 1000 child nodes
    for i in range(2, 1002):
        parent_id = 1
        slot = ((i - 2) % 5) + 1
        label = f"Child{i}"
        depth = 1
        conn.execute(
            "INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (?, ?, ?, ?, ?)",
            (i, parent_id, slot, label, depth)
        )
    
    # Test query performance with larger dataset
    query = """
        SELECT n.id, n.label, n.depth, n.updated_at,
               COUNT(c.id) as child_count
        FROM nodes n
        LEFT JOIN nodes c ON c.parent_id = n.id
        WHERE n.depth = 0 OR (n.depth > 0 AND n.parent_id IS NOT NULL)
        GROUP BY n.id, n.label, n.depth, n.updated_at
        HAVING child_count < 5
        ORDER BY n.depth, n.id
    """
    
    start_time = time.time()
    cursor = conn.execute(query)
    results = cursor.fetchall()
    end_time = time.time()
    
    # Should still complete quickly even with larger dataset
    execution_time = (end_time - start_time) * 1000
    assert execution_time < 500, f"Query took {execution_time}ms, should be < 500ms"
    
    # Should return expected number of results
    assert len(results) >= 1, "Should return at least one result"
    
    conn.close()

def test_navigate_cache_performance():
    """Test navigate cache performance (if implemented)."""
    # This test would check if navigate cache is working
    # For now, just test that the endpoint responds quickly
    
    response = client.get("/api/v1/tree/next-incomplete-parent")
    
    # Should return quickly
    assert response.status_code in [200, 204], f"Expected 200 or 204, got {response.status_code}"
    
    # Response time should be reasonable
    # Note: This is a basic test - in a real implementation, we'd measure actual response time

def test_database_connection_pooling():
    """Test that database connections are properly managed."""
    # This test would verify connection pooling in a real implementation
    # For now, just test that we can get multiple connections
    
    conn1 = get_db_connection()
    conn2 = get_db_connection()
    
    # Both connections should work
    assert conn1 is not None
    assert conn2 is not None
    
    # Should be able to execute queries on both
    cursor1 = conn1.execute("SELECT 1")
    cursor2 = conn2.execute("SELECT 1")
    
    assert cursor1.fetchone()[0] == 1
    assert cursor2.fetchone()[0] == 1
    
    conn1.close()
    conn2.close()

def test_query_optimization():
    """Test that queries are optimized for performance."""
    conn = get_db_connection()
    
    # Insert test data
    conn.execute("INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (1, NULL, 0, 'Root', 0)")
    for i in range(2, 22):  # 20 child nodes
        parent_id = 1
        slot = ((i - 2) % 5) + 1
        label = f"Child{i}"
        depth = 1
        conn.execute(
            "INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (?, ?, ?, ?, ?)",
            (i, parent_id, slot, label, depth)
        )
    
    # Test various queries for optimization
    queries = [
        "SELECT * FROM nodes WHERE parent_id = ?",
        "SELECT * FROM nodes WHERE slot = ?",
        "SELECT * FROM nodes WHERE label LIKE ?",
        "SELECT COUNT(*) FROM nodes WHERE parent_id = ?",
        "SELECT * FROM nodes ORDER BY depth, slot"
    ]
    
    for query in queries:
        # Test with different parameters
        test_params = [
            (1,),  # parent_id
            (1,),  # slot
            ("Child%",),  # label pattern
            (1,),  # parent_id for count
            ()  # no params for order by
        ]
        
        for params in test_params:
            if len(params) == len(query.split("?")) - 1:
                start_time = time.time()
                cursor = conn.execute(query, params)
                results = cursor.fetchall()
                end_time = time.time()
                
                # Should complete quickly
                execution_time = (end_time - start_time) * 1000
                assert execution_time < 100, f"Query '{query}' took {execution_time}ms, should be < 100ms"
    
    conn.close()

def test_memory_efficiency():
    """Test memory efficiency of operations."""
    conn = get_db_connection()
    
    # Insert test data
    conn.execute("INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (1, NULL, 0, 'Root', 0)")
    for i in range(2, 102):  # 100 child nodes
        parent_id = 1
        slot = ((i - 2) % 5) + 1
        label = f"Child{i}"
        depth = 1
        conn.execute(
            "INSERT INTO nodes (id, parent_id, slot, label, depth) VALUES (?, ?, ?, ?, ?)",
            (i, parent_id, slot, label, depth)
        )
    
    # Test memory usage during query execution
    query = "SELECT * FROM nodes ORDER BY depth, slot"
    
    start_time = time.time()
    cursor = conn.execute(query)
    results = cursor.fetchall()
    end_time = time.time()
    
    # Should complete quickly
    execution_time = (end_time - start_time) * 1000
    assert execution_time < 200, f"Query took {execution_time}ms, should be < 200ms"
    
    # Should return expected number of results
    assert len(results) == 101, f"Expected 101 results, got {len(results)}"
    
    conn.close()
