"""
Tests for flag audit pruning functionality.
"""

import pytest
import sqlite3
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from ops.prune_flags import prune_flag_audit


class TestFlagAuditPruning:
    """Test flag audit table pruning."""

    def test_prune_by_age(self, tmp_path):
        """Test pruning rows older than max_age_days."""
        # Create test database
        db_path = tmp_path / "test.db"

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Create flag_audit table
            cursor.execute("""
                CREATE TABLE flag_audit (
                    id INTEGER PRIMARY KEY,
                    node_id INTEGER,
                    flag_id INTEGER,
                    action TEXT,
                    ts TEXT
                )
            """)

            # Insert test data
            now = datetime.now(timezone.utc)
            old_date = (now - timedelta(days=60)).isoformat().replace("+00:00", "Z")
            new_date = (now - timedelta(days=10)).isoformat().replace("+00:00", "Z")

            # Insert old records (should be deleted)
            for i in range(10):
                cursor.execute(
                    "INSERT INTO flag_audit (node_id, flag_id, action, ts) VALUES (?, ?, ?, ?)",
                    (i, 1, 'assign', old_date)
                )

            # Insert new records (should be kept)
            for i in range(10):
                cursor.execute(
                    "INSERT INTO flag_audit (node_id, flag_id, action, ts) VALUES (?, ?, ?, ?)",
                    (i + 10, 1, 'assign', new_date)
                )

            conn.commit()

        # Mock the database path in SQLiteRepository
        with patch('storage.sqlite.SQLiteRepository.get_resolved_db_path', return_value=str(db_path)):
            result = prune_flag_audit(max_age_days=30)

            assert result["success"] is True
            assert result["rows_before"] == 20
            assert result["rows_deleted"] == 10
            assert result["rows_after"] == 10

    def test_prune_by_row_limit(self, tmp_path):
        """Test pruning when exceeding max_rows limit."""
        # Create test database
        db_path = tmp_path / "test.db"

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Create flag_audit table
            cursor.execute("""
                CREATE TABLE flag_audit (
                    id INTEGER PRIMARY KEY,
                    node_id INTEGER,
                    flag_id INTEGER,
                    action TEXT,
                    ts TEXT
                )
            """)

            # Insert test data (more than max_rows)
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            for i in range(100):  # More than default max_rows of 50000
                cursor.execute(
                    "INSERT INTO flag_audit (node_id, flag_id, action, ts) VALUES (?, ?, ?, ?)",
                    (i, 1, 'assign', now)
                )

            conn.commit()

        # Mock the database path
        with patch('storage.sqlite.SQLiteRepository.get_resolved_db_path', return_value=str(db_path)):
            result = prune_flag_audit(max_rows=50)

            assert result["success"] is True
            assert result["rows_before"] == 100
            assert result["rows_deleted"] == 50
            assert result["rows_after"] == 50

    def test_no_pruning_needed(self, tmp_path):
        """Test when no pruning is needed."""
        # Create test database
        db_path = tmp_path / "test.db"

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Create flag_audit table
            cursor.execute("""
                CREATE TABLE flag_audit (
                    id INTEGER PRIMARY KEY,
                    node_id INTEGER,
                    flag_id INTEGER,
                    action TEXT,
                    ts TEXT
                )
            """)

            # Insert recent data (within 30 days)
            now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

            for i in range(10):
                cursor.execute(
                    "INSERT INTO flag_audit (node_id, flag_id, action, ts) VALUES (?, ?, ?, ?)",
                    (i, 1, 'assign', now)
                )

            conn.commit()

        # Mock the database path
        with patch('storage.sqlite.SQLiteRepository.get_resolved_db_path', return_value=str(db_path)):
            result = prune_flag_audit(max_age_days=30)

            assert result["success"] is True
            assert result["rows_before"] == 10
            assert result["rows_deleted"] == 0
            assert result["rows_after"] == 10

    def test_table_not_exists(self, tmp_path):
        """Test when flag_audit table doesn't exist."""
        # Create test database without flag_audit table
        db_path = tmp_path / "test.db"

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE some_other_table (id INTEGER)")

        # Mock the database path
        with patch('storage.sqlite.SQLiteRepository.get_resolved_db_path', return_value=str(db_path)):
            result = prune_flag_audit()

            assert "tables_exist" in result
            assert result["tables_exist"] is False
            assert result["rows_deleted"] == 0

    def test_empty_table(self, tmp_path):
        """Test when flag_audit table exists but is empty."""
        # Create test database with empty flag_audit table
        db_path = tmp_path / "test.db"

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE flag_audit (
                    id INTEGER PRIMARY KEY,
                    node_id INTEGER,
                    flag_id INTEGER,
                    action TEXT,
                    ts TEXT
                )
            """)

        # Mock the database path
        with patch('storage.sqlite.SQLiteRepository.get_resolved_db_path', return_value=str(db_path)):
            result = prune_flag_audit()

            assert result["success"] is True
            assert result["rows_before"] == 0
            assert result["rows_deleted"] == 0
            assert result["rows_after"] == 0
