"""
Test that Streamlit pages only use API calls and don't have forbidden imports.
"""

import pathlib
import re

# Forbidden imports that would bypass the API
FORBIDDEN = (
    r'\bsqlite3\b',      # Direct database access
    r'\bsqlalchemy\b',   # ORM that could access DB
    r'\bpandas\b',       # Data manipulation that could read files
    r'\bopenpyxl\b',     # Excel reading that could bypass API
    r'\bgspread\b',      # Google Sheets access
)

# Streamlit directories to check
PAGES_DIRS = ["ui_streamlit", "ui_streamlit/pages"]

def test_streamlit_has_no_forbidden_imports():
    """Ensure Streamlit pages don't have forbidden imports that bypass the API."""
    roots = [pathlib.Path(p) for p in PAGES_DIRS if pathlib.Path(p).exists()]
    assert roots, "Streamlit directories not found"
    
    bad_imports = []
    
    for root in roots:
        for py_file in root.rglob("*.py"):
            # Skip __init__.py and other non-page files
            if py_file.name.startswith("__"):
                continue
                
            try:
                text = py_file.read_text(encoding="utf-8", errors="ignore")
                
                # Check for forbidden imports
                for pattern in FORBIDDEN:
                    if re.search(pattern, text):
                        bad_imports.append((str(py_file), pattern))
                        
            except Exception as e:
                # Skip files that can't be read
                continue
    
    assert not bad_imports, f"Forbidden imports found: {bad_imports}"


def test_streamlit_uses_api_client():
    """Ensure Streamlit pages import from the API client."""
    api_client_imports = []
    
    for root_name in PAGES_DIRS:
        root = pathlib.Path(root_name)
        if not root.exists():
            continue
            
        for py_file in root.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            try:
                text = py_file.read_text(encoding="utf-8", errors="ignore")
                
                # Check if file imports from api_client
                if "from ui_streamlit.api_client import" in text or "import ui_streamlit.api_client" in text:
                    api_client_imports.append(str(py_file))
                    
            except Exception:
                continue
    
    # At least some pages should use the API client
    assert len(api_client_imports) > 0, "No Streamlit pages found using the API client"
