"""
Pytest configuration for Lorien tests.
"""

import pytest
import os
from unittest.mock import patch

@pytest.fixture(autouse=True)
def enable_llm_for_tests():
    """Enable LLM for all tests by default."""
    with patch.dict(os.environ, {"LLM_ENABLED": "true"}):
        yield
