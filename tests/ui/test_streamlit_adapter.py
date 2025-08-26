#!/usr/bin/env python3
"""
Smoke test for Streamlit adapter.

Tests that the Streamlit app can start and displays health/version information.
"""

import pytest
import subprocess
import time
import requests
import tempfile
import os
import signal
from pathlib import Path
from typing import Generator


class TestStreamlitAdapter:
    """Test the Streamlit adapter functionality."""
    
    @pytest.fixture
    def temp_db_path(self) -> Generator[str, None, None]:
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        yield db_path
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def mock_api_server(self) -> Generator[str, None, None]:
        """Start a mock API server for testing."""
        # Create a simple mock API server
        mock_server_code = '''
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/api/v1/health")
async def health():
    return JSONResponse({
        "ok": True,
        "version": "6.6.0",
        "db": {
            "wal": True,
            "foreign_keys": True,
            "page_size": 4096,
            "path": "/tmp/test.db"
        },
        "features": {"llm": False}
    })

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
'''
        
        # Write mock server to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
            tmp_file.write(mock_server_code)
            mock_server_path = tmp_file.name
        
        # Start mock server
        mock_process = subprocess.Popen(
            ["python", mock_server_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(2)
        
        yield "http://127.0.0.1:8001"
        
        # Cleanup
        mock_process.terminate()
        mock_process.wait()
        os.unlink(mock_server_path)
    
    def test_streamlit_app_imports(self):
        """Test that the Streamlit app can be imported without errors."""
        try:
            # Add the ui_streamlit directory to the path
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ui_streamlit"))
            
            # Import the app
            import app
            assert hasattr(app, 'StreamlitAdapter')
            assert hasattr(app, 'main')
            
        except ImportError as e:
            pytest.fail(f"Failed to import Streamlit app: {e}")
    
    def test_streamlit_adapter_health_check(self, temp_db_path):
        """Test that the Streamlit adapter can perform health checks."""
        # Set up environment
        os.environ['DB_PATH'] = temp_db_path
        
        try:
            # Import the adapter
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ui_streamlit"))
            from app import StreamlitAdapter
            
            # Test local services mode
            adapter = StreamlitAdapter("http://localhost:8000")
            health = adapter.get_health()
            
            # Basic health check
            assert isinstance(health, dict)
            assert "version" in health
            assert "db" in health
            
        except Exception as e:
            pytest.fail(f"Health check failed: {e}")
    
    def test_streamlit_adapter_api_mode(self, mock_api_server):
        """Test that the Streamlit adapter can connect to API."""
        try:
            # Import the adapter
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ui_streamlit"))
            from app import StreamlitAdapter
            
            # Test API mode
            adapter = StreamlitAdapter(mock_api_server)
            health = adapter.get_health()
            
            # Verify API response
            assert health.get("ok") is True
            assert health.get("version") == "6.6.0"
            assert health.get("db", {}).get("wal") is True
            
        except Exception as e:
            pytest.fail(f"API mode test failed: {e}")
    
    def test_streamlit_app_starts_without_errors(self):
        """Test that the Streamlit app can start without immediate errors."""
        # This is a basic smoke test - we don't actually run the full Streamlit app
        # because it requires a GUI environment, but we can test the initialization
        
        try:
            # Import the app
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ui_streamlit"))
            from app import StreamlitAdapter, main
            
            # Test that we can create an adapter
            adapter = StreamlitAdapter()
            assert adapter is not None
            
            # Test that main function exists and is callable
            assert callable(main)
            
        except Exception as e:
            pytest.fail(f"Streamlit app initialization failed: {e}")
    
    def test_streamlit_config_exists(self):
        """Test that the Streamlit config file exists and has correct settings."""
        config_path = Path(__file__).parent.parent.parent / "ui_streamlit" / ".streamlit" / "config.toml"
        
        assert config_path.exists(), f"Streamlit config not found at {config_path}"
        
        # Read and verify config contents
        config_content = config_path.read_text()
        
        # Check for required settings
        assert "fileWatcherType = \"poll\"" in config_content
        assert "runOnSave = false" in config_content
        assert "serverAddress = \"localhost\"" in config_content
        assert "serverPort = 8501" in config_content
    
    def test_streamlit_app_structure(self):
        """Test that the Streamlit app has the expected structure."""
        app_path = Path(__file__).parent.parent.parent / "ui_streamlit" / "app.py"
        
        assert app_path.exists(), f"Streamlit app not found at {app_path}"
        
        # Read and verify app structure
        app_content = app_path.read_text()
        
        # Check for required components
        assert "class StreamlitAdapter" in app_content
        assert "def main()" in app_content
        assert "st.set_page_config" in app_content
        assert "APP_VERSION" in app_content
        assert "DEV ADAPTER" in app_content
        
        # Check that it uses core services or API calls
        assert "from core.services.tree_service import TreeService" in app_content
        assert "from storage.sqlite import SQLiteRepository" in app_content
        assert "requests.get" in app_content
        
        # Check that it doesn't have direct database or Google Sheets calls
        assert "gspread" not in app_content
        assert "sqlite3.connect" not in app_content  # Should use repository instead


if __name__ == "__main__":
    pytest.main([__file__])
