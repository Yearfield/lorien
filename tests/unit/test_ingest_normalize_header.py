import pytest

from Engines.EngineLongBow.ingest import CANON, HeaderMismatchError, normalize_header


def test_normalize_header_canonical():
    """Test that canonical header passes through unchanged."""
    canonical = ["D0", "D1", "D2", "D3", "D4", "D5", "D6", "Notes"]
    result = normalize_header(canonical)
    assert result == canonical


def test_normalize_header_synonyms():
    """Test that synonym headers are normalized correctly."""
    synonym_header = [
        "Vital Measurement",
        "Node 1",
        "Node 2",
        "Node 3",
        "Node 4",
        "Node 5",
        "Diagnostic Triage",
        "Actions",
    ]
    result = normalize_header(synonym_header)
    assert result == CANON


def test_normalize_header_mixed_case_spaces():
    """Test that mixed case and extra spaces are handled."""
    messy_header = [
        "  vital measurement  ",
        "NODE 1",
        "node  2",
        "Node 3",
        "node4",
        "Node 5",
        "DIAGNOSTIC TRIAGE",
        "actions  ",
    ]
    result = normalize_header(messy_header)
    assert result == CANON


def test_normalize_header_shuffled_raises():
    """Test that shuffled columns raise an error."""
    shuffled = ["D1", "D0", "D2", "D3", "D4", "D5", "D6", "Notes"]  # D0 and D1 swapped
    with pytest.raises(HeaderMismatchError) as exc_info:
        normalize_header(shuffled)
    assert "Columns must map to D0..D5, D6, Notes structure" in exc_info.value.hint


def test_normalize_header_unknown_raises():
    """Test that unknown headers raise an error with helpful hint."""
    unknown = ["Unknown", "D1", "D2", "D3", "D4", "D5", "D6", "Notes"]
    with pytest.raises(HeaderMismatchError) as exc_info:
        normalize_header(unknown)
    assert "Accepted synonyms:" in exc_info.value.hint
    assert "vitalmeasurement" in exc_info.value.hint
