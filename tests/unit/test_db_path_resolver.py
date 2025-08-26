#!/usr/bin/env python3
"""
Unit tests for database path resolver.

Tests OS-specific database path resolution and environment variable overrides.
"""

import pytest
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from storage.sqlite import SQLiteRepository


class TestDatabasePathResolver:
    """Test database path resolution functionality."""
    
    def test_windows_path_resolution(self):
        """Test database path resolution on Windows."""
        with patch('os.name', 'nt'), \
             patch('sys.platform', 'win32'), \
             patch.dict(os.environ, {'APPDATA': 'C:\\Users\\TestUser\\AppData\\Roaming'}), \
             patch.object(SQLiteRepository, '_init_database'):
            
            repo = SQLiteRepository()
            expected_path = os.path.join('C:\\Users\\TestUser\\AppData\\Roaming', 'lorien', 'app.db')
            assert repo.get_resolved_db_path() == expected_path
    
    def test_macos_path_resolution(self):
        """Test database path resolution on macOS."""
        with patch('os.name', 'posix'), \
             patch('sys.platform', 'darwin'), \
             patch('os.path.expanduser', return_value='/Users/TestUser'), \
             patch('os.makedirs'), \
             patch.object(SQLiteRepository, '_init_database'):
            
            repo = SQLiteRepository()
            expected_path = os.path.join('/Users/TestUser', 'Library', 'Application Support', 'lorien', 'app.db')
            assert repo.get_resolved_db_path() == expected_path
    
    def test_linux_path_resolution(self):
        """Test database path resolution on Linux."""
        with patch('os.name', 'posix'), \
             patch('sys.platform', 'linux'), \
             patch('os.path.expanduser', return_value='/home/testuser'), \
             patch('os.makedirs'), \
             patch.object(SQLiteRepository, '_init_database'):
            
            repo = SQLiteRepository()
            expected_path = os.path.join('/home/testuser', '.local', 'share', 'lorien', 'app.db')
            assert repo.get_resolved_db_path() == expected_path
    
    def test_environment_variable_override(self):
        """Test that DB_PATH environment variable overrides default path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = os.path.join(temp_dir, 'database.db')
            
            with patch.dict(os.environ, {'DB_PATH': custom_path}), \
                 patch.object(SQLiteRepository, '_init_database'):
                repo = SQLiteRepository()
                assert repo.get_resolved_db_path() == custom_path
    
    def test_environment_variable_override_with_none(self):
        """Test that None DB_PATH doesn't cause issues."""
        with patch.dict(os.environ, {}, clear=True), \
             patch.object(SQLiteRepository, '_init_database'):
            repo = SQLiteRepository()
            # Should not raise an exception
            path = repo.get_resolved_db_path()
            assert path is not None
            assert isinstance(path, str)
    
    def test_directory_creation(self):
        """Test that database directory is created if it doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = os.path.join(temp_dir, 'nonexistent', 'subdir', 'app.db')
            
            with patch.dict(os.environ, {'DB_PATH': custom_path}), \
                 patch.object(SQLiteRepository, '_init_database'):
                repo = SQLiteRepository()
                
                # Directory should be created
                db_dir = os.path.dirname(custom_path)
                assert os.path.exists(db_dir)
    
    def test_app_name_is_lorien(self):
        """Test that the app name is 'lorien' (lowercase)."""
        with patch('os.name', 'posix'), \
             patch('sys.platform', 'linux'), \
             patch('os.path.expanduser', return_value='/home/testuser'), \
             patch('os.makedirs'), \
             patch.object(SQLiteRepository, '_init_database'):
            
            repo = SQLiteRepository()
            path = repo.get_resolved_db_path()
            
            # Check that 'lorien' appears in the path
            assert 'lorien' in path
            # Check that it's lowercase
            assert 'lorien' in path.lower()
    
    def test_database_filename_is_app_db(self):
        """Test that the database filename is 'app.db'."""
        with patch('os.name', 'posix'), \
             patch('sys.platform', 'linux'), \
             patch('os.path.expanduser', return_value='/home/testuser'), \
             patch('os.makedirs'), \
             patch.object(SQLiteRepository, '_init_database'):
            
            repo = SQLiteRepository()
            path = repo.get_resolved_db_path()
            
            # Check that the filename is 'app.db'
            assert path.endswith('app.db')
    
    def test_multiple_instances_same_path(self):
        """Test that multiple repository instances use the same path."""
        with patch('os.name', 'posix'), \
             patch('sys.platform', 'linux'), \
             patch('os.path.expanduser', return_value='/home/testuser'), \
             patch('os.makedirs'), \
             patch.object(SQLiteRepository, '_init_database'):
            
            repo1 = SQLiteRepository()
            repo2 = SQLiteRepository()
            
            path1 = repo1.get_resolved_db_path()
            path2 = repo2.get_resolved_db_path()
            
            assert path1 == path2
    
    def test_custom_db_path_constructor(self):
        """Test that custom db_path in constructor overrides everything."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = os.path.join(temp_dir, 'constructor.db')
            env_path = os.path.join(temp_dir, 'env.db')
            
            with patch.dict(os.environ, {'DB_PATH': env_path}), \
                 patch.object(SQLiteRepository, '_init_database'):
                repo = SQLiteRepository(db_path=custom_path)
                assert repo.get_resolved_db_path() == custom_path
    
    def test_unknown_platform_fallback(self):
        """Test fallback behavior for unknown platforms."""
        with patch('os.name', 'unknown'), \
             patch('sys.platform', 'unknown'), \
             patch('os.path.expanduser', return_value='/home/testuser'), \
             patch('os.makedirs'), \
             patch.object(SQLiteRepository, '_init_database'):
            
            repo = SQLiteRepository()
            path = repo.get_resolved_db_path()
            
            # Should fall back to Linux-style path
            expected_path = os.path.join('/home/testuser', '.local', 'share', 'lorien', 'app.db')
            assert path == expected_path
    
    def test_path_resolution_with_special_characters(self):
        """Test path resolution with special characters in username."""
        with patch('os.name', 'posix'), \
             patch('sys.platform', 'linux'), \
             patch('os.path.expanduser', return_value='/home/user with spaces'), \
             patch('os.makedirs'), \
             patch.object(SQLiteRepository, '_init_database'):
            
            repo = SQLiteRepository()
            path = repo.get_resolved_db_path()
            
            expected_path = os.path.join('/home/user with spaces', '.local', 'share', 'lorien', 'app.db')
            assert path == expected_path
    
    def test_environment_variable_priority(self):
        """Test that environment variable takes priority over platform detection."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = os.path.join(temp_dir, 'env.db')
            
            with patch('os.name', 'posix'), \
                 patch('sys.platform', 'linux'), \
                 patch('os.path.expanduser', return_value='/home/testuser'), \
                 patch.dict(os.environ, {'DB_PATH': custom_path}), \
                 patch('os.makedirs'), \
                 patch.object(SQLiteRepository, '_init_database'):
                
                repo = SQLiteRepository()
                assert repo.get_resolved_db_path() == custom_path


if __name__ == "__main__":
    pytest.main([__file__])
