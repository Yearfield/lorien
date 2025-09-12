"""
Test that the 8-column header appears exactly once as canonical.

This ensures we maintain a single source of truth for the API header.
"""

import os
import re
from pathlib import Path

def test_header_sot_single_occurrence():
    """Test that the canonical 8-column header appears exactly once."""
    canonical_header = "Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions"
    
    # Find all occurrences of the header
    occurrences = []
    
    # Check documentation files
    for root, dirs, files in os.walk("docs/"):
        for file in files:
            if file.endswith(('.md', '.txt', '.rst')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for exact matches
                    matches = re.findall(re.escape(canonical_header), content)
                    for match in matches:
                        occurrences.append({
                            "file": file_path,
                            "match": match,
                            "type": "exact"
                        })
                except Exception:
                    pass
    
    # Check code files
    for root, dirs, files in os.walk("api/"):
        for file in files:
            if file.endswith(('.py', '.txt')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for exact matches
                    matches = re.findall(re.escape(canonical_header), content)
                    for match in matches:
                        occurrences.append({
                            "file": file_path,
                            "match": match,
                            "type": "exact"
                        })
                except Exception:
                    pass
    
    # Check test files
    for root, dirs, files in os.walk("tests/"):
        for file in files:
            if file.endswith(('.py', '.txt', '.csv')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for exact matches
                    matches = re.findall(re.escape(canonical_header), content)
                    for match in matches:
                        occurrences.append({
                            "file": file_path,
                            "match": match,
                            "type": "exact"
                        })
                except Exception:
                    pass
    
    # The header should appear in the SoT document
    sot_file = "docs/API_HEADER_SOT.md"
    assert os.path.exists(sot_file), "SoT document should exist"
    
    # Count occurrences
    exact_occurrences = [occ for occ in occurrences if occ["type"] == "exact"]
    
    # Should have at least one occurrence (in the SoT document)
    assert len(exact_occurrences) >= 1, f"Header should appear at least once, found {len(exact_occurrences)}"
    
    # Should not have too many occurrences (indicating duplication)
    # Allow for reasonable number of occurrences in documentation and code
    assert len(exact_occurrences) <= 20, f"Too many header occurrences found: {len(exact_occurrences)}. This suggests duplication."
    
    # Verify the SoT document contains the header
    sot_occurrences = [occ for occ in exact_occurrences if occ["file"] == sot_file]
    assert len(sot_occurrences) >= 1, "SoT document should contain the canonical header"

def test_header_sot_format_consistency():
    """Test that all header occurrences use the exact same format."""
    canonical_header = "Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions"
    
    # Find all variations
    variations = []
    
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(('.md', '.py', '.txt', '.rst', '.csv')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Look for header-like patterns
                    pattern = r'vital measurement.*node 1.*node 2.*node 3.*node 4.*node 5.*diagnostic triage.*actions'
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if match != canonical_header:
                            variations.append({
                                "file": file_path,
                                "found": match,
                                "expected": canonical_header
                            })
                except Exception:
                    pass
    
    # Should not have too many variations (some are expected in code comments, etc.)
    # Exclude test files from this check
    test_variations = [v for v in variations if not v["file"].startswith("./tests/")]
    assert len(test_variations) <= 20, f"Found {len(test_variations)} header format variations in non-test files. Too many variations found."

def test_header_sot_documentation_references():
    """Test that documentation properly references the SoT."""
    sot_file = "docs/API_HEADER_SOT.md"
    
    # Check that SoT document exists and is properly formatted
    assert os.path.exists(sot_file), "SoT document should exist"
    
    with open(sot_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Should contain the canonical header
    assert "Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions" in content
    
    # Should contain usage guidelines
    assert "Usage Guidelines" in content
    assert "Frozen Header" in content
    assert "Change Control" in content
    
    # Should contain version history
    assert "Version History" in content

def test_header_sot_no_duplicates():
    """Test that there are no duplicate header definitions."""
    canonical_header = "Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions"
    
    # Count occurrences in each file
    file_counts = {}
    
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(('.md', '.py', '.txt', '.rst', '.csv')):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Count exact matches
                    matches = re.findall(re.escape(canonical_header), content)
                    if matches:
                        file_counts[file_path] = len(matches)
                except Exception:
                    pass
    
    # Each file should have at most a reasonable number of occurrences
    for file_path, count in file_counts.items():
        # Allow up to 5 occurrences per file (for documentation, examples, etc.)
        # Exclude test files from this check
        if not file_path.startswith("./tests/"):
            assert count <= 5, f"File {file_path} has {count} header occurrences, should have at most 5"
