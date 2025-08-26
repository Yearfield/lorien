#!/usr/bin/env python3
"""
Integration tests for backup and restore scripts.

Tests the actual backup and restore functionality using temporary databases.
"""

import pytest
import os
import sys
import tempfile
import subprocess
import sqlite3
import time
import glob
from pathlib import Path
from unittest.mock import patch

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from storage.sqlite import SQLiteRepository


class TestBackupRestore:
    """Integration tests for backup and restore functionality."""
    
    @pytest.fixture
    def temp_db_with_data(self, tmp_path):
        """
        Creates a temp file DB, applies schema via SQLiteRepository, seeds one node,
        then COMMITS & CLOSES the connection to ensure the file is fully written
        before backup/restore scripts run.
        Returns (db_path, repo_placeholder, node_id). repo_placeholder is None after close.
        """
        db_path = str(tmp_path / "app.db")

        # Create repo and schema
        repo = SQLiteRepository(db_path=db_path)

        # Seed minimal data using repo methods
        from core.models import Node
        from datetime import datetime
        
        test_node = Node(
            id=None,
            parent_id=None,
            depth=0,
            slot=0,
            label="Root A",
            is_leaf=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        node_id = repo.create_node(test_node)
        print(f"Test node created with ID: {node_id}")

        # COMMIT & CLOSE to flush the file to disk
        try:
            repo.close()
        except Exception:
            pass

        # Sanity: file size should now exceed the header-only 4096 bytes
        size = os.path.getsize(db_path)
        print(f"[fixture] DB path: {db_path}")
        print(f"[fixture] DB size after close: {size} bytes")
        assert size > 4096, "DB file appears empty; ensure commit/close happened"

        # Ensure scripts use this DB path
        os.environ["DB_PATH"] = db_path

        # Return (db_path, repo_placeholder, node_id); repo is closed, so pass None
        yield (db_path, None, node_id)
    
    @pytest.fixture
    def scripts_dir(self):
        """Get the scripts directory path."""
        return project_root / "tools" / "scripts"
    
    def test_backup_script_creates_backup(self, temp_db_with_data, scripts_dir):
        """Test that backup script creates a backup file."""
        db_path, repo, node_id = temp_db_with_data
        
        # Set environment variable to use our test database
        env = os.environ.copy()
        env['DB_PATH'] = db_path
        
        # Run backup script
        result = subprocess.run(
            [str(scripts_dir / "backup_db.sh")],
            capture_output=True,
            text=True,
            env=env,
            cwd=project_root
        )
        
        # Check script ran successfully
        assert result.returncode == 0, f"Backup script failed: {result.stderr}"
        
        # Check output contains success message (strip color codes for comparison)
        import re
        clean_stdout = re.sub(r'\x1b\[[0-9;]*m', '', result.stdout)
        assert "[SUCCESS] Backup created:" in clean_stdout, f"Expected '[SUCCESS] Backup created:' in output. Raw output: {result.stdout}"
        
        # Find the backup file (there might be multiple from previous tests)
        backup_dir = os.path.dirname(db_path)
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith("lorien_backup_")]
        
        assert len(backup_files) >= 1, f"Expected at least 1 backup file, found {len(backup_files)}"
        # Use the most recent backup file
        backup_files.sort()
        backup_path = os.path.join(backup_dir, backup_files[-1])
        
        # Verify backup file exists and has same size
        assert os.path.exists(backup_path)
        assert os.path.getsize(backup_path) == os.path.getsize(db_path)
        
        # Clean up backup file
        os.unlink(backup_path)
    
    def test_backup_script_with_custom_directory(self, temp_db_with_data, scripts_dir):
        """Test backup script with custom target directory."""
        db_path, repo, node_id = temp_db_with_data
        
        # Create temporary directory for backup
        with tempfile.TemporaryDirectory() as backup_dir:
            env = os.environ.copy()
            env['DB_PATH'] = db_path
            
            # Run backup script with custom directory
            result = subprocess.run(
                [str(scripts_dir / "backup_db.sh"), backup_dir],
                capture_output=True,
                text=True,
                env=env,
                cwd=project_root
            )
            
            # Check script ran successfully
            assert result.returncode == 0, f"Backup script failed: {result.stderr}"
            
            # Check backup was created in custom directory
            backup_files = [f for f in os.listdir(backup_dir) if f.startswith("lorien_backup_")]
            assert len(backup_files) == 1
    
    def test_restore_script_restores_data(self, temp_db_with_data, scripts_dir):
        """Test that restore script restores data correctly."""
        db_path, repo, node_id = temp_db_with_data
        
        # Create a backup first
        env = os.environ.copy()
        env['DB_PATH'] = db_path
        
        # Create backup
        print(f"Running backup script with DB_PATH={env['DB_PATH']}")
        
        # Show directory contents before backup
        print(f"[test] Directory contents before backup:")
        for p in sorted(glob.glob(os.path.join(os.path.dirname(db_path), "*"))):
            try:
                print(" -", os.path.basename(p), os.path.getsize(p), "bytes")
            except Exception:
                print(" -", os.path.basename(p), "(size n/a)")
        
        result = subprocess.run(
            [str(scripts_dir / "backup_db.sh")],
            capture_output=True,
            text=True,
            env=env,
            cwd=project_root
        )
        print(f"Backup script stdout: {result.stdout}")
        print(f"Backup script stderr: {result.stderr}")
        print(f"Backup script return code: {result.returncode}")
        
        # Find the backup file (there might be multiple from previous tests)
        backup_dir = os.path.dirname(db_path)
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith("lorien_backup_")]
        # Use the most recent backup file
        backup_files.sort()
        backup_path = os.path.join(backup_dir, backup_files[-1])
        
        # Modify the original database to verify restore
        with sqlite3.connect(db_path) as conn:
            conn.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
            conn.commit()
        
        # Verify data was deleted
        with sqlite3.connect(db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM nodes WHERE id = ?", (node_id,))
            count = cursor.fetchone()[0]
            assert count == 0
        
        # Restore from backup
        print(f"Running restore script with backup: {backup_path}")
        result = subprocess.run(
            [str(scripts_dir / "restore_db.sh"), backup_path],
            capture_output=True,
            text=True,
            env=env,
            cwd=project_root
        )
        
        # Check script ran successfully
        print(f"Restore script stdout: {result.stdout}")
        print(f"Restore script stderr: {result.stderr}")
        print(f"Restore script return code: {result.returncode}")
        assert result.returncode == 0, f"Restore script failed: {result.stderr}"
        
        # Verify data was restored using a fresh connection
        
        # Optional small delay on CI/WSL to allow file system events to settle
        time.sleep(0.1)
        
        print(f"[test] Listing target dir after restore:")
        for p in sorted(glob.glob(os.path.join(os.path.dirname(db_path), "*"))):
            try:
                print(" -", os.path.basename(p), os.path.getsize(p), "bytes")
            except Exception:
                print(" -", os.path.basename(p), "(size n/a)")
        
        with sqlite3.connect(db_path) as conn:
            cnt = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
            print(f"[test] Node count after restore: {cnt}")
            assert cnt >= 1, "Restore did not bring back expected rows from backup"
        
        # Clean up backup file
        os.unlink(backup_path)
    
    def test_restore_script_creates_backup_of_current(self, temp_db_with_data, scripts_dir):
        """Test that restore script creates backup of current database."""
        db_path, repo, node_id = temp_db_with_data
        
        # Create a backup first
        env = os.environ.copy()
        env['DB_PATH'] = db_path
        
        # Create backup
        subprocess.run(
            [str(scripts_dir / "backup_db.sh")],
            capture_output=True,
            text=True,
            env=env,
            cwd=project_root
        )
        
        # Find the backup file (there might be multiple from previous tests)
        backup_dir = os.path.dirname(db_path)
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith("lorien_backup_")]
        # Use the most recent backup file
        backup_files.sort()
        backup_path = os.path.join(backup_dir, backup_files[-1])
        
        # Restore from backup
        result = subprocess.run(
            [str(scripts_dir / "restore_db.sh"), backup_path],
            capture_output=True,
            text=True,
            env=env,
            cwd=project_root
        )
        
        # Check script ran successfully
        assert result.returncode == 0, f"Restore script failed: {result.stderr}"
        
        # Check that a backup of the current database was created
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith("app.db.bak.")]
        assert len(backup_files) == 1
        
        # Clean up backup files
        os.unlink(backup_path)
        os.unlink(os.path.join(backup_dir, backup_files[0]))
    
    def test_backup_script_nonexistent_database(self, scripts_dir):
        """Test backup script with nonexistent database."""
        # Use a database path that doesn't exist
        nonexistent_db = "/tmp/nonexistent/lorien/app.db"
        
        env = os.environ.copy()
        env['DB_PATH'] = nonexistent_db
        
        # Run backup script
        result = subprocess.run(
            [str(scripts_dir / "backup_db.sh")],
            capture_output=True,
            text=True,
            env=env,
            cwd=project_root
        )
        
        # Script should exit successfully (it creates the directory structure)
        assert result.returncode == 0
        # The script creates the directory and database, so it should succeed
        assert "Backup created successfully!" in result.stdout
    
    def test_restore_script_invalid_backup_file(self, scripts_dir):
        """Test restore script with invalid backup file."""
        # Create an invalid backup file
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            invalid_backup = tmp_file.name
            tmp_file.write(b"This is not a valid SQLite database")
        
        try:
            # Run restore script
            result = subprocess.run(
                [str(scripts_dir / "restore_db.sh"), invalid_backup],
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            # Script should fail
            assert result.returncode != 0
            assert "Invalid backup file" in result.stderr or "Invalid backup file" in result.stdout or "Invalid SQLite database" in result.stderr
        
        finally:
            # Clean up
            os.unlink(invalid_backup)
    
    def test_backup_script_help(self, scripts_dir):
        """Test backup script help functionality."""
        result = subprocess.run(
            [str(scripts_dir / "backup_db.sh"), "--help"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        assert result.returncode == 0
        assert "Usage:" in result.stdout
        assert "Creates a timestamped backup" in result.stdout
    
    def test_restore_script_help(self, scripts_dir):
        """Test restore script help functionality."""
        result = subprocess.run(
            [str(scripts_dir / "restore_db.sh"), "--help"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        assert result.returncode == 0
        assert "Usage:" in result.stdout
        assert "Restores a Lorien database" in result.stdout
    
    def test_backup_script_missing_python(self, temp_db_with_data, scripts_dir):
        """Test backup script behavior when Python is not available."""
        db_path, repo, node_id = temp_db_with_data
        
        env = os.environ.copy()
        env['DB_PATH'] = db_path
        env['PATH'] = '/nonexistent/path'  # Remove Python from PATH
        
        # Run backup script
        result = subprocess.run(
            [str(scripts_dir / "backup_db.sh")],
            capture_output=True,
            text=True,
            env=env,
            cwd=project_root
        )
        
        # Script should fail
        assert result.returncode != 0
        assert "Python 3 is required" in result.stderr or "Python 3 is required" in result.stdout
    
    def test_restore_script_missing_backup_file(self, scripts_dir):
        """Test restore script with missing backup file."""
        result = subprocess.run(
            [str(scripts_dir / "restore_db.sh")],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        # Script should fail
        assert result.returncode != 0
        assert "Backup file path is required" in result.stderr or "Backup file path is required" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__])
