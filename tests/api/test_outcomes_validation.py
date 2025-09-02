"""
Tests for outcomes validation with normalization, word caps, regex, and dosing token bans.
"""

import pytest
from core.validation.outcomes import (
    normalize, validate_field, validate_outcomes, clamp_llm_suggestion,
    FieldError, PROHIBITED_TOKENS, PROHIBITED_DOSE, WHITELIST, MAX_WORDS
)


class TestOutcomesNormalization:
    """Tests for outcomes normalization."""
    
    def test_normalize_trims_edges(self):
        """Test that normalization trims leading and trailing whitespace."""
        assert normalize("  test  ") == "test"
        assert normalize("\t\n test \n\t") == "test"
    
    def test_normalize_collapses_whitespace(self):
        """Test that normalization collapses internal whitespace runs."""
        assert normalize("test   with    spaces") == "test with spaces"
        assert normalize("test\t\twith\n\nnewlines") == "test with newlines"
    
    def test_normalize_handles_empty(self):
        """Test that normalization handles empty and None values."""
        assert normalize("") == ""
        assert normalize(None) == ""
        assert normalize("   ") == ""


class TestOutcomesValidation:
    """Tests for outcomes validation."""
    
    def test_validate_field_empty_after_normalization(self):
        """Test that empty fields after normalization raise error."""
        with pytest.raises(FieldError) as exc_info:
            validate_field("test_field", "   ")
        
        error = exc_info.value
        assert error.field == "test_field"
        assert error.message == "must not be empty"
        assert error.error_type == "value_error.empty"
    
    def test_validate_field_word_count_limit(self):
        """Test that fields with >7 words raise error."""
        long_text = "word1 word2 word3 word4 word5 word6 word7 word8"
        
        with pytest.raises(FieldError) as exc_info:
            validate_field("test_field", long_text)
        
        error = exc_info.value
        assert error.field == "test_field"
        assert error.message == f"must be ≤{MAX_WORDS} words"
        assert error.error_type == "value_error.word_count"
    
    def test_validate_field_regex_whitelist(self):
        """Test that fields with invalid characters raise error."""
        invalid_texts = [
            "test with @ symbol",
            "test with ! exclamation",
            "test with # hash",
            "test with $ dollar",
            "test with & ampersand",
            "test with * asterisk",
            "test with ( parentheses",
            "test with ) parentheses",
            "test with + plus",
            "test with = equals",
            "test with { brace",
            "test with } brace",
            "test with | pipe",
            "test with \\ backslash",
            "test with : colon",
            "test with ; semicolon",
            "test with \" quote",
            "test with ' apostrophe",
            "test with < less",
            "test with > greater",
            "test with ? question",
            "test with / slash",
            "test with ~ tilde",
            "test with ` backtick",
        ]
        
        for invalid_text in invalid_texts:
            with pytest.raises(FieldError) as exc_info:
                validate_field("test_field", invalid_text)
            
            error = exc_info.value
            assert error.field == "test_field"
            assert error.message == "invalid characters"
            assert error.error_type == "value_error.regex"
    
    def test_validate_field_prohibited_dosing_tokens(self):
        """Test that fields with prohibited dosing tokens raise error."""
        prohibited_texts = [
            "take 10 mg daily",
            "inject 5 mcg",
            "apply 2.5 µg",
            "use 100 ug",
            "drink 250 ml",
            "weigh 50 g",
            "measure 1 kg",
            "administer 1000 IU",
            "give 2 units",
            "dilute to 5%",
            "take bid",
            "apply tid",
            "use qid",
            "take q4h",
            "apply qhs",
            "use prn",
            "take po",
            "inject iv",
            "apply im",
            "use sc",
            "inject subcut",
            "take tds",
            "apply od",
            "use bd",
        ]
        
        for prohibited_text in prohibited_texts:
            with pytest.raises(FieldError) as exc_info:
                validate_field("test_field", prohibited_text)
            
            error = exc_info.value
            assert error.field == "test_field"
            assert "prohibited" in error.message.lower()
            assert error.error_type == "value_error.prohibited_token"
    
    def test_validate_field_prohibited_dosing_patterns(self):
        """Test that fields with prohibited dosing patterns raise error."""
        prohibited_patterns = [
            "take 10mg daily",
            "inject 5mcg",
            "apply 2.5µg",
            "use 100ug",
            "drink 250ml",
            "weigh 50g",
            "measure 1kg",
            "administer 1000IU",
            "give 2units",
            "dilute to 5%",
            "take 10.5 mg",
            "inject 2.25 mcg",
            "apply 1.75 µg",
        ]
        
        for prohibited_pattern in prohibited_patterns:
            with pytest.raises(FieldError) as exc_info:
                validate_field("test_field", prohibited_pattern)
            
            error = exc_info.value
            assert error.field == "test_field"
            assert "prohibited" in error.message.lower()
            assert error.error_type == "value_error.prohibited_token"
    
    def test_validate_field_valid_inputs(self):
        """Test that valid inputs pass validation."""
        valid_inputs = [
            "monitor patient",
            "check vital signs",
            "assess condition",
            "review history",
            "document findings",
            "follow up",
            "continue treatment",
            "discharge patient",
            "refer to specialist",
            "schedule appointment",
            "patient stable",
            "no acute distress",
            "normal findings",
            "improvement noted",
            "recovery expected",
        ]
        
        for valid_input in valid_inputs:
            result = validate_field("test_field", valid_input)
            assert result == normalize(valid_input)
    
    def test_validate_outcomes_both_fields(self):
        """Test validation of both diagnostic_triage and actions fields."""
        # Valid inputs
        triage, actions = validate_outcomes("monitor patient", "check vitals")
        assert triage == "monitor patient"
        assert actions == "check vitals"
        
        # Invalid triage
        with pytest.raises(FieldError) as exc_info:
            validate_outcomes("take 10 mg daily", "check vitals")
        
        error = exc_info.value
        assert error.field == "diagnostic_triage"
        assert error.error_type == "value_error.prohibited_token"
        
        # Invalid actions
        with pytest.raises(FieldError) as exc_info:
            validate_outcomes("monitor patient", "inject 5 mcg")
        
        error = exc_info.value
        assert error.field == "actions"
        assert error.error_type == "value_error.prohibited_token"


class TestLLMSuggestionClamping:
    """Tests for LLM suggestion clamping."""
    
    def test_clamp_llm_suggestion_empty(self):
        """Test clamping empty suggestions."""
        assert clamp_llm_suggestion("") == ""
        assert clamp_llm_suggestion(None) == ""
        assert clamp_llm_suggestion("   ") == ""
    
    def test_clamp_llm_suggestion_word_limit(self):
        """Test that suggestions are truncated to 7 words."""
        long_suggestion = "word1 word2 word3 word4 word5 word6 word7 word8 word9"
        clamped = clamp_llm_suggestion(long_suggestion)
        
        words = clamped.split()
        assert len(words) <= MAX_WORDS
        assert clamped == "word1 word2 word3 word4 word5 word6 word7"
    
    def test_clamp_llm_suggestion_removes_prohibited_tokens(self):
        """Test that prohibited tokens are removed from suggestions."""
        suggestion_with_tokens = "monitor patient take 10 mg daily"
        clamped = clamp_llm_suggestion(suggestion_with_tokens)
        
        assert "mg" not in clamped
        assert "monitor patient" in clamped
        assert "[dosing]" in clamped  # "10 mg" should be replaced with "[dosing]"
    
    def test_clamp_llm_suggestion_removes_prohibited_patterns(self):
        """Test that prohibited patterns are removed from suggestions."""
        suggestion_with_patterns = "inject 5mcg and monitor"
        clamped = clamp_llm_suggestion(suggestion_with_patterns)
        
        assert "5mcg" not in clamped
        assert "monitor" in clamped
        assert "[dosing]" in clamped  # "5mcg" should be replaced with "[dosing]"
    
    def test_clamp_llm_suggestion_whitelist_characters(self):
        """Test that only whitelist characters are kept."""
        suggestion_with_bad_chars = "monitor patient @#$%^&*()"
        clamped = clamp_llm_suggestion(suggestion_with_bad_chars)
        
        # Should only contain whitelist characters
        import re
        assert re.fullmatch(WHITELIST, clamped)
        assert "monitor patient" in clamped
    
    def test_clamp_llm_suggestion_normalizes(self):
        """Test that suggestions are normalized."""
        suggestion_with_whitespace = "  monitor   patient  "
        clamped = clamp_llm_suggestion(suggestion_with_whitespace)
        
        assert clamped == "monitor patient"
    
    def test_clamp_llm_suggestion_valid_input(self):
        """Test that valid inputs pass through unchanged."""
        valid_suggestion = "monitor patient condition"
        clamped = clamp_llm_suggestion(valid_suggestion)
        
        assert clamped == valid_suggestion
