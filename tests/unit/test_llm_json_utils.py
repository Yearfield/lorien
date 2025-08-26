import pytest
from llm.json_utils import extract_first_json, parse_fill_response, clamp

class TestExtractFirstJSON:
    def test_extract_valid_json(self):
        text = 'Some text {"diagnostic_triage": "test", "actions": "action"} more text'
        result = extract_first_json(text)
        assert result == '{"diagnostic_triage": "test", "actions": "action"}'
    
    def test_extract_json_with_newlines(self):
        text = '''Some text
        {
            "diagnostic_triage": "test",
            "actions": "action"
        }
        more text'''
        result = extract_first_json(text)
        assert '"diagnostic_triage"' in result
        assert '"actions"' in result
    
    def test_no_json_found(self):
        text = 'Just some text without JSON'
        result = extract_first_json(text)
        assert result is None
    
    def test_empty_string(self):
        result = extract_first_json("")
        assert result is None

class TestParseFillResponse:
    def test_parse_valid_json(self):
        json_str = '{"diagnostic_triage": "Test triage", "actions": "Test actions"}'
        dt, ac = parse_fill_response(json_str)
        assert dt == "Test triage"
        assert ac == "Test actions"
    
    def test_parse_json_with_extra_text(self):
        text = 'Here is the response: {"diagnostic_triage": "Test", "actions": "Action"} and more text'
        dt, ac = parse_fill_response(text)
        assert dt == "Test"
        assert ac == "Action"
    
    def test_parse_missing_keys(self):
        json_str = '{"diagnostic_triage": "Only triage"}'
        dt, ac = parse_fill_response(json_str)
        assert dt == "Only triage"
        assert ac == ""
    
    def test_parse_invalid_json(self):
        text = 'Invalid JSON: {diagnostic_triage: "test"}'
        dt, ac = parse_fill_response(text)
        assert dt == ""
        assert ac == ""
    
    def test_parse_empty_string(self):
        dt, ac = parse_fill_response("")
        assert dt == ""
        assert ac == ""

class TestClamp:
    def test_clamp_short_text(self):
        result = clamp("Short text", 20)
        assert result == "Short text"
    
    def test_clamp_long_text(self):
        result = clamp("This is a very long text that should be clamped", 20)
        assert len(result) <= 20
        assert result.endswith("…")
    
    def test_clamp_empty_string(self):
        result = clamp("", 10)
        assert result == ""
    
    def test_clamp_none(self):
        result = clamp(None, 10)
        assert result == ""
    
    def test_clamp_exact_length(self):
        text = "Exactly ten"
        result = clamp(text, 11)
        assert result == text
