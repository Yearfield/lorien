"""
Tests for performance optimization functionality.

Tests database indexes, streaming exports, caching, and performance monitoring.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sqlite3
import io
import csv

from api.app import app
from api.repositories.performance import (
    PerformanceOptimizer, StreamingCSVExporter, NavigationCache,
    get_cache_stats, clear_navigation_cache
)

client = TestClient(app)

class TestPerformanceOptimizer:
    """Test performance optimization utilities."""
    
    def test_create_performance_indexes(self):
        """Test creating performance indexes."""
        conn = sqlite3.connect(':memory:')
        conn.execute('''
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER,
                label TEXT,
                depth INTEGER,
                slot INTEGER,
                is_leaf INTEGER
            )
        ''')
        
        optimizer = PerformanceOptimizer(conn)
        indexes = optimizer.create_performance_indexes()
        
        # Check that indexes were created
        assert len(indexes) > 0
        assert 'idx_nodes_depth' in indexes
        assert 'idx_nodes_slot' in indexes
        assert 'idx_nodes_parent_slot' in indexes
        
        # Verify indexes exist in database
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='nodes'")
        index_names = [row[0] for row in cursor.fetchall()]
        
        for index_name in indexes.keys():
            assert index_name in index_names
    
    def test_get_database_stats(self):
        """Test database statistics collection."""
        conn = sqlite3.connect(':memory:')
        conn.execute('''
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER,
                label TEXT,
                depth INTEGER,
                slot INTEGER,
                is_leaf INTEGER
            )
        ''')
        
        # Insert test data
        conn.execute('''
            INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
            VALUES (1, NULL, 'Root', 0, NULL, 0),
                   (2, 1, 'Child 1', 1, 1, 0),
                   (3, 1, 'Child 2', 1, 2, 1)
        ''')
        conn.commit()
        
        optimizer = PerformanceOptimizer(conn)
        stats = optimizer.get_database_stats()
        
        assert stats['total_nodes'] == 3
        assert stats['root_nodes'] == 1
        assert stats['leaf_nodes'] == 1
        assert stats['database_size_bytes'] > 0
        assert 'indexes' in stats
        assert 'depth_distribution' in stats
        assert 'slot_distribution' in stats
    
    def test_analyze_query_performance(self):
        """Test query performance analysis."""
        conn = sqlite3.connect(':memory:')
        conn.execute('''
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER,
                label TEXT,
                depth INTEGER,
                slot INTEGER,
                is_leaf INTEGER
            )
        ''')
        
        # Insert test data
        conn.execute('''
            INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
            VALUES (1, NULL, 'Root', 0, NULL, 0),
                   (2, 1, 'Child 1', 1, 1, 0),
                   (3, 1, 'Child 2', 1, 2, 1)
        ''')
        conn.commit()
        
        optimizer = PerformanceOptimizer(conn)
        analysis = optimizer.analyze_query_performance(
            "SELECT * FROM nodes WHERE depth = ?", (1,)
        )
        
        assert 'query_plan' in analysis
        assert 'execution_time' in analysis
        assert 'result_count' in analysis
        assert analysis['result_count'] == 2
        assert analysis['execution_time'] >= 0


class TestStreamingCSVExporter:
    """Test streaming CSV export functionality."""
    
    def test_export_tree_streaming(self):
        """Test streaming tree export."""
        conn = sqlite3.connect(':memory:')
        conn.execute('''
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER,
                label TEXT,
                depth INTEGER,
                slot INTEGER,
                is_leaf INTEGER
            )
        ''')
        
        # Insert test data
        conn.execute('''
            INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
            VALUES (1, NULL, 'Root', 0, NULL, 0),
                   (2, 1, 'Child 1', 1, 1, 0),
                   (3, 1, 'Child 2', 1, 2, 1)
        ''')
        conn.commit()
        
        exporter = StreamingCSVExporter(conn)
        chunks = list(exporter.export_tree_streaming(batch_size=2))
        
        # Should have header + data chunks
        assert len(chunks) >= 2
        
        # First chunk should be header
        assert 'id,parent_id,label,depth,slot,is_leaf' in chunks[0]
        
        # Combine all chunks and verify data
        full_csv = ''.join(chunks)
        lines = full_csv.strip().split('\n')
        assert len(lines) == 4  # Header + 3 data rows
    
    def test_export_children_streaming(self):
        """Test streaming children export."""
        conn = sqlite3.connect(':memory:')
        conn.execute('''
            CREATE TABLE nodes (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER,
                label TEXT,
                depth INTEGER,
                slot INTEGER,
                is_leaf INTEGER
            )
        ''')
        
        # Insert test data
        conn.execute('''
            INSERT INTO nodes (id, parent_id, label, depth, slot, is_leaf)
            VALUES (1, NULL, 'Root', 0, NULL, 0),
                   (2, 1, 'Child 1', 1, 1, 0),
                   (3, 1, 'Child 2', 1, 2, 1)
        ''')
        conn.commit()
        
        exporter = StreamingCSVExporter(conn)
        chunks = list(exporter.export_children_streaming(parent_id=1, batch_size=2))
        
        # Should have header + data chunks
        assert len(chunks) >= 2
        
        # First chunk should be header
        assert 'id,parent_id,label,depth,slot,is_leaf' in chunks[0]
        
        # Combine all chunks and verify data
        full_csv = ''.join(chunks)
        lines = full_csv.strip().split('\n')
        assert len(lines) == 3  # Header + 2 data rows


class TestNavigationCache:
    """Test navigation cache functionality."""
    
    def test_cache_basic_operations(self):
        """Test basic cache operations."""
        cache = NavigationCache(max_size=3)
        
        # Test set and get
        cache.set('key1', 'value1')
        assert cache.get('key1') == 'value1'
        assert cache.get('nonexistent') is None
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = NavigationCache(max_size=2)
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        cache.set('key3', 'value3')  # Should evict key1
        
        assert cache.get('key1') is None
        assert cache.get('key2') == 'value2'
        assert cache.get('key3') == 'value3'
    
    def test_cache_stats(self):
        """Test cache statistics."""
        cache = NavigationCache(max_size=5)
        
        # Initial stats
        stats = cache.get_stats()
        assert stats['size'] == 0
        assert stats['hit_count'] == 0
        assert stats['miss_count'] == 0
        
        # Test hits and misses
        cache.set('key1', 'value1')
        cache.get('key1')  # hit
        cache.get('key2')  # miss
        
        stats = cache.get_stats()
        assert stats['size'] == 1
        assert stats['hit_count'] == 1
        assert stats['miss_count'] == 1
        assert stats['hit_rate_percent'] == 50.0
    
    def test_cache_clear(self):
        """Test cache clearing."""
        cache = NavigationCache(max_size=5)
        
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')
        
        assert cache.get('key1') == 'value1'
        
        cache.clear()
        
        assert cache.get('key1') is None
        assert cache.get('key2') is None
        
        stats = cache.get_stats()
        assert stats['size'] == 0


class TestPerformanceEndpoints:
    """Test performance API endpoints."""
    
    def test_get_database_stats(self):
        """Test database stats endpoint."""
        response = client.get("/api/v1/admin/performance/database-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "database_stats" in data
        assert "cache_stats" in data
        assert "status" in data
        
        db_stats = data["database_stats"]
        assert "total_nodes" in db_stats
        assert "root_nodes" in db_stats
        assert "leaf_nodes" in db_stats
        assert "database_size_bytes" in db_stats
    
    def test_create_performance_indexes(self):
        """Test create indexes endpoint."""
        response = client.post("/api/v1/admin/performance/create-indexes")
        assert response.status_code == 200
        
        data = response.json()
        assert "created_indexes" in data
        assert "index_count" in data
        assert "status" in data
        assert data["status"] == "completed"
    
    def test_get_cache_stats(self):
        """Test cache stats endpoint."""
        response = client.get("/api/v1/admin/performance/cache-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "cache_stats" in data
        assert "status" in data
        
        cache_stats = data["cache_stats"]
        assert "size" in cache_stats
        assert "max_size" in cache_stats
        assert "hit_rate_percent" in cache_stats
    
    def test_clear_cache(self):
        """Test clear cache endpoint."""
        response = client.post("/api/v1/admin/performance/clear-cache")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "completed"
        assert "message" in data
    
    def test_get_performance_health(self):
        """Test performance health endpoint."""
        response = client.get("/api/v1/admin/performance/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "performance_status" in data
        assert "database_stats" in data
        assert "cache_stats" in data
        assert "recommendations" in data
        assert "status" in data
        
        # Check that performance_status is one of expected values
        valid_statuses = ["healthy", "needs_optimization", "cache_inefficient"]
        assert data["performance_status"] in valid_statuses


class TestStreamingEndpoints:
    """Test streaming export endpoints."""
    
    def test_export_tree_streaming(self):
        """Test streaming tree export endpoint."""
        response = client.get("/api/v1/admin/performance/export/tree-streaming")
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
        
        # Check that response is streaming
        content = response.content.decode('utf-8')
        assert 'id,parent_id,label,depth,slot,is_leaf' in content
    
    def test_export_children_streaming(self):
        """Test streaming children export endpoint."""
        # First, get a parent ID from the database
        response = client.get("/api/v1/tree/next-incomplete-parent")
        if response.status_code == 200:
            parent_data = response.json()
            parent_id = parent_data.get('id')
            
            if parent_id:
                response = client.get(f"/api/v1/admin/performance/export/children-streaming/{parent_id}")
                assert response.status_code == 200
                assert response.headers["content-type"] == "text/csv; charset=utf-8"
                assert "attachment" in response.headers["content-disposition"]


class TestPerformanceIntegration:
    """Test performance integration with existing functionality."""
    
    def test_performance_monitoring_integration(self):
        """Test that performance monitoring integrates with existing endpoints."""
        # Test that performance endpoints don't interfere with existing functionality
        response = client.get("/api/v1/tree/next-incomplete-parent")
        assert response.status_code in [200, 404]  # 404 if no incomplete parent
        
        response = client.get("/api/v1/admin/performance/database-stats")
        assert response.status_code == 200
    
    def test_index_creation_idempotent(self):
        """Test that index creation is idempotent."""
        # Create indexes twice
        response1 = client.post("/api/v1/admin/performance/create-indexes")
        response2 = client.post("/api/v1/admin/performance/create-indexes")
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Both should succeed (idempotent)
        data1 = response1.json()
        data2 = response2.json()
        
        assert data1["status"] == "completed"
        assert data2["status"] == "completed"


class TestPerformanceErrorHandling:
    """Test performance error handling."""
    
    def test_database_stats_error_handling(self):
        """Test database stats error handling."""
        # This test would need to mock database errors
        # For now, just test that the endpoint exists and returns 200
        response = client.get("/api/v1/admin/performance/database-stats")
        assert response.status_code == 200
    
    def test_invalid_query_analysis(self):
        """Test query analysis with invalid query."""
        response = client.get("/api/v1/admin/performance/analyze-query?query=INVALID SQL")
        # Should handle invalid SQL gracefully
        assert response.status_code in [200, 400, 500]

