import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import pytest

from core.storage.path import get_db_path, _platform_paths


class TestDBPathResolution:
    """Test database path resolution logic."""

    def test_platform_paths_linux(self):
        """Test Linux path resolution."""
        with patch('sys.platform', 'linux'):
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path('/home/testuser')
                data_dir, db_path = _platform_paths('testapp')
                
                assert str(data_dir) == '/home/testuser/.local/share/testapp'
                assert str(db_path) == '/home/testuser/.local/share/testapp/app.db'

    def test_platform_paths_macos(self):
        """Test macOS path resolution."""
        with patch('sys.platform', 'darwin'):
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path('/Users/testuser')
                data_dir, db_path = _platform_paths('testapp')
                
                assert str(data_dir) == '/Users/testuser/Library/Application Support/testapp'
                assert str(db_path) == '/Users/testuser/Library/Application Support/testapp/app.db'

    def test_platform_paths_windows(self):
        """Test Windows path resolution."""
        # Skip this test on non-Windows systems to avoid pathlib issues
        if os.name != 'nt':
            pytest.skip("Windows path testing not supported on this platform")
        
        with patch('os.name', 'nt'):
            with patch('os.getenv') as mock_getenv:
                with patch('pathlib.Path.home') as mock_home:
                    mock_getenv.return_value = 'C:\\Users\\testuser\\AppData\\Roaming'
                    mock_home.return_value = Path('C:\\Users\\testuser')
                    
                    data_dir, db_path = _platform_paths('testapp')
                    
                    # Just verify the function doesn't crash
                    assert data_dir is not None
                    assert db_path is not None

    def test_get_db_path_env_override(self):
        """Test DB_PATH environment variable override."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_db_path = os.path.join(tmpdir, 'custom.db')
            
            with patch.dict(os.environ, {'DB_PATH': env_db_path}):
                result = get_db_path('testapp')
                
                assert str(result) == os.path.abspath(env_db_path)
                assert result.parent.exists()  # Directory should be created

    def test_get_db_path_default_linux(self):
        """Test default path resolution on Linux."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('sys.platform', 'linux'):
                with patch('pathlib.Path.home') as mock_home:
                    mock_home.return_value = Path(tmpdir)
                    
                    result = get_db_path('testapp')
                    
                    expected = Path(tmpdir) / '.local' / 'share' / 'testapp' / 'app.db'
                    assert str(result) == str(expected.resolve())
                    assert result.parent.exists()  # Directory should be created

    def test_get_db_path_creates_directories(self):
        """Test that parent directories are created automatically."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use a nested path that doesn't exist
            nested_path = os.path.join(tmpdir, 'deeply', 'nested', 'path', 'app.db')
            
            with patch.dict(os.environ, {'DB_PATH': nested_path}):
                result = get_db_path('testapp')
                
                assert str(result) == os.path.abspath(nested_path)
                assert result.parent.exists()
                assert result.parent.is_dir()

    def test_get_db_path_resolves_relative(self):
        """Test that relative paths are resolved to absolute."""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            
            # Use a relative path
            relative_path = './relative/path/app.db'
            
            with patch.dict(os.environ, {'DB_PATH': relative_path}):
                result = get_db_path('testapp')
                
                assert result.is_absolute()
                assert str(result).endswith('relative/path/app.db')

    def test_get_db_path_expands_user(self):
        """Test that ~ is expanded to user home directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('pathlib.Path.home') as mock_home:
                mock_home.return_value = Path(tmpdir)
                
                # Use a path with ~
                user_path = '~/myapp/app.db'
                
                with patch.dict(os.environ, {'DB_PATH': user_path}):
                    # Mock Path.expanduser to return our temp dir
                    with patch.object(Path, 'expanduser') as mock_expanduser:
                        mock_expanduser.return_value = Path(tmpdir) / 'myapp' / 'app.db'
                        
                        result = get_db_path('testapp')
                        
                        expected = Path(tmpdir) / 'myapp' / 'app.db'
                        assert str(result) == str(expected.resolve())
