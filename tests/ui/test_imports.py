import os
import sys
from pathlib import Path

def test_ui_streamlit_package_importable():
    """Test that ui_streamlit package can be imported without errors."""
    # Simulate the launcher environment by adding repo root to sys.path
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    
    # Test basic package import
    import ui_streamlit  # noqa: F401
    
    # Test key module imports
    from ui_streamlit import components  # noqa: F401
    from ui_streamlit import api_client  # noqa: F401
    from ui_streamlit import settings  # noqa: F401
    
    # Test that we can access key functions
    from ui_streamlit.settings import get_api_base_url
    from ui_streamlit.components import top_health_banner
    from ui_streamlit.api_client import get_health
    
    # Verify the functions exist and are callable
    assert callable(get_api_base_url)
    assert callable(top_health_banner)
    assert callable(get_health)
    
    # Test that default API base URL is correct
    default_url = get_api_base_url()
    assert "/api/v1" in default_url, f"Expected /api/v1 in default URL, got: {default_url}"
