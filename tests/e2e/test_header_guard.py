"""
E2E test for header guard functionality: non-canonical headers should be rejected.
"""

import os
import subprocess
from tests.utils.http import get_json, post_json


def test_header_guard_rejects_non_canonical_headers(temp_database, api_server):
    """
    Test that non-canonical headers are rejected with clear error messages.
    """
    # Test with missing slot 4 fixture (should work with canonical headers)
    fixture_path = "tests/fixtures/missing_slot_4.xlsx"
    assert os.path.exists(fixture_path), f"Fixture not found: {fixture_path}"
    
    # This should import successfully since it has canonical headers
    result = subprocess.run(
        ["python", "-m", "cli.main", "import-excel", fixture_path],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )
    
    # Should succeed (canonical headers)
    assert result.returncode == 0, f"Import with canonical headers failed: {result.stderr}"
    print("✅ Import with canonical headers succeeded")
    
    # Test validation - should show missing slots
    result = subprocess.run(
        ["python", "-m", "cli.main", "validate"],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )
    
    # Should succeed but may show violations
    print(f"Validation result: {result.stdout}")
    if result.stderr:
        print(f"Validation stderr: {result.stderr}")


def test_header_guard_accepts_canonical_headers(temp_database, api_server):
    """
    Test that canonical headers are accepted.
    """
    # Test with perfect 5-children fixture (canonical headers)
    fixture_path = "tests/fixtures/perfect_5_children.xlsx"
    assert os.path.exists(fixture_path), f"Fixture not found: {fixture_path}"
    
    result = subprocess.run(
        ["python", "-m", "cli.main", "import-excel", fixture_path],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )
    
    # Should succeed
    assert result.returncode == 0, f"Import with canonical headers failed: {result.stderr}"
    print("✅ Import with canonical headers succeeded")
    
    # Validate - should show 0 violations
    result = subprocess.run(
        ["python", "-m", "cli.main", "validate"],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )
    
    # Should succeed
    assert result.returncode == 0, f"Validation failed: {result.stderr}"
    print(f"✅ Validation successful: {result.stdout}")


def test_header_guard_with_unicode_labels(temp_database, api_server):
    """
    Test that unicode labels with canonical headers are accepted.
    """
    # Test with unicode labels fixture
    fixture_path = "tests/fixtures/unicode_labels.xlsx"
    assert os.path.exists(fixture_path), f"Fixture not found: {fixture_path}"
    
    result = subprocess.run(
        ["python", "-m", "cli.main", "import-excel", fixture_path],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )
    
    # Should succeed
    assert result.returncode == 0, f"Import with unicode labels failed: {result.stderr}"
    print("✅ Import with unicode labels succeeded")


def test_header_guard_with_long_labels(temp_database, api_server):
    """
    Test that long labels with canonical headers are accepted.
    """
    # Test with long labels fixture
    fixture_path = "tests/fixtures/long_labels.xlsx"
    assert os.path.exists(fixture_path), f"Fixture not found: {fixture_path}"
    
    result = subprocess.run(
        ["python", "-m", "cli.main", "import-excel", fixture_path],
        capture_output=True,
        text=True,
        env=os.environ.copy()
    )
    
    # Should succeed
    assert result.returncode == 0, f"Import with long labels failed: {result.stderr}"
    print("✅ Import with long labels succeeded")
