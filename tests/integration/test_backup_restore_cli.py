import os
import tempfile
import sqlite3
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from tools.cli import cmd_backup, cmd_restore, cmd_show_db_path, cmd_wal_checkpoint


class TestBackupRestoreCLI:
    """Test backup and restore CLI functionality."""

    def test_show_db_path(self, capsys):
        """Test show-db-path command."""
        with patch('tools.cli.get_db_path') as mock_get_path:
            mock_get_path.return_value = Path('/test/path/app.db')
            
            cmd_show_db_path(None)
            
            captured = capsys.readouterr()
            assert captured.out.strip() == '/test/path/app.db'

    def test_backup_creates_file(self, tmp_path):
        """Test backup command creates backup file."""
        # Create a test database
        db_path = tmp_path / "test.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.execute("INSERT INTO test (id) VALUES (1)")
            conn.commit()
        
        # Mock get_db_path to return our test DB
        with patch('tools.cli.get_db_path') as mock_get_path:
            mock_get_path.return_value = db_path
            
            # Mock sqlite3 command availability
            with patch('tools.cli._ensure_sqlite3', return_value=False):
                # Create args object
                args = MagicMock()
                args.target = None
                
                cmd_backup(args)
                
                # Check that backup was created
                backup_files = list(tmp_path.glob("lorien_backup_*.db"))
                assert len(backup_files) == 1
                
                backup_path = backup_files[0]
                assert backup_path.exists()
                
                # Check backup size > 4096 (has data)
                size = backup_path.stat().st_size
                assert size > 4096, f"Backup size {size} should be > 4096 bytes"

    def test_backup_with_custom_target(self, tmp_path):
        """Test backup command with custom target."""
        # Create a test database
        db_path = tmp_path / "test.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.execute("INSERT INTO test (id) VALUES (1)")
            conn.commit()
        
        # Mock get_db_path to return our test DB
        with patch('tools.cli.get_db_path') as mock_get_path:
            mock_get_path.return_value = db_path
            
            # Mock sqlite3 command availability
            with patch('tools.cli._ensure_sqlite3', return_value=False):
                # Create args object with custom target
                args = MagicMock()
                args.target = str(tmp_path / "custom_backup.db")
                
                cmd_backup(args)
                
                # Check that custom backup was created
                backup_path = tmp_path / "custom_backup.db"
                assert backup_path.exists()
                
                # Check backup size > 4096 (has data)
                size = backup_path.stat().st_size
                assert size > 4096, f"Backup size {size} should be > 4096 bytes"

    def test_backup_db_not_found(self, capsys):
        """Test backup command when database doesn't exist."""
        with patch('tools.cli.get_db_path') as mock_get_path:
            mock_get_path.return_value = Path('/nonexistent/path/app.db')
            
            # Create args object
            args = MagicMock()
            args.target = None
            
            with pytest.raises(SystemExit) as exc_info:
                cmd_backup(args)
            
            assert exc_info.value.code == 1
            
            captured = capsys.readouterr()
            assert "DB not found" in captured.err

    def test_restore_restores_data(self, tmp_path):
        """Test restore command restores data correctly."""
        # Create a test database with data
        db_path = tmp_path / "test.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO test (id, name) VALUES (1, 'test data')")
            conn.commit()
        
        # Create a backup
        backup_path = tmp_path / "backup.db"
        with sqlite3.connect(backup_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            conn.execute("INSERT INTO test (id, name) VALUES (1, 'test data')")
            conn.commit()
        
        # Mock get_db_path to return our test DB
        with patch('tools.cli.get_db_path') as mock_get_path:
            mock_get_path.return_value = db_path
            
            # Mock sqlite3 command availability
            with patch('tools.cli._ensure_sqlite3', return_value=False):
                # Create args object
                args = MagicMock()
                args.backup = str(backup_path)
                
                # Delete the original data
                db_path.unlink()
                
                # Restore from backup
                cmd_restore(args)
                
                # Check that data was restored
                assert db_path.exists()
                
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM test")
                    count = cursor.fetchone()[0]
                    assert count == 1
                    
                    cursor = conn.execute("SELECT id FROM test WHERE id = 1")
                    id_val = cursor.fetchone()[0]
                    assert id_val == 1

    def test_restore_backup_not_found(self, capsys):
        """Test restore command when backup doesn't exist."""
        with patch('tools.cli.get_db_path') as mock_get_path:
            mock_get_path.return_value = Path('/test/path/app.db')
            
            # Create args object with nonexistent backup
            args = MagicMock()
            args.backup = '/nonexistent/backup.db'
            
            with pytest.raises(SystemExit) as exc_info:
                cmd_restore(args)
            
            assert exc_info.value.code == 1
            
            captured = capsys.readouterr()
            assert "Backup not found" in captured.err

    def test_wal_checkpoint(self, tmp_path):
        """Test WAL checkpoint command."""
        # Create a test database
        db_path = tmp_path / "test.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.execute("INSERT INTO test (id) VALUES (1)")
            conn.commit()
        
        # Mock get_db_path to return our test DB
        with patch('tools.cli.get_db_path') as mock_get_path:
            mock_get_path.return_value = db_path
            
            # Create args object
            args = MagicMock()
            
            # Should not raise any exceptions
            cmd_wal_checkpoint(args)
            
            # Database should still exist and be accessible
            assert db_path.exists()
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM test")
                count = cursor.fetchone()[0]
                assert count == 1

    def test_backup_uses_sqlite3_when_available(self, tmp_path, capsys):
        """Test backup command uses sqlite3 .backup when available."""
        # Create a test database
        db_path = tmp_path / "test.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.execute("INSERT INTO test (id) VALUES (1)")
            conn.commit()
        
        # Mock get_db_path to return our test DB
        with patch('tools.cli.get_db_path') as mock_get_path:
            mock_get_path.return_value = db_path
            
            # Mock sqlite3 command availability
            with patch('tools.cli._ensure_sqlite3', return_value=True):
                # Mock os.system to capture the command
                with patch('os.system') as mock_system:
                    # Create args object
                    args = MagicMock()
                    args.target = None
                    
                    cmd_backup(args)
                    
                    # Check that sqlite3 .backup was called
                    mock_system.assert_called_once()
                    call_args = mock_system.call_args[0][0]
                    assert "sqlite3" in call_args
                    assert ".backup" in call_args

    def test_restore_uses_sqlite3_when_available(self, tmp_path, capsys):
        """Test restore command uses sqlite3 .restore when available."""
        # Create a test database
        db_path = tmp_path / "test.db"
        with sqlite3.connect(db_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.execute("INSERT INTO test (id) VALUES (1)")
            conn.commit()
        
        # Create a backup
        backup_path = tmp_path / "backup.db"
        with sqlite3.connect(backup_path) as conn:
            conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
            conn.execute("INSERT INTO test (id) VALUES (1)")
            conn.commit()
        
        # Mock get_db_path to return our test DB
        with patch('tools.cli.get_db_path') as mock_get_path:
            mock_get_path.return_value = db_path
            
            # Mock sqlite3 command availability
            with patch('tools.cli._ensure_sqlite3', return_value=True):
                # Mock os.system to capture the command
                with patch('os.system') as mock_system:
                    # Create args object
                    args = MagicMock()
                    args.backup = str(backup_path)
                    
                    # Delete the original data
                    db_path.unlink()
                    
                    cmd_restore(args)
                    
                    # Check that sqlite3 .restore was called
                    mock_system.assert_called()
                    # Should be called at least once for the restore
                    restore_calls = [call for call in mock_system.call_args_list if '.restore' in call[0][0]]
                    assert len(restore_calls) > 0
