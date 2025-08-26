import pytest
from llm.safety import safety_gate, SafetyResult

class TestSafetyGate:
    def test_safe_content(self):
        """Test that safe content is allowed."""
        safe_texts = [
            "Patient reports mild headache",
            "Consider evaluation for abdominal pain",
            "Monitor symptoms and follow up",
            "May benefit from specialist consultation"
        ]
        
        for text in safe_texts:
            result = safety_gate(text)
            assert result.allowed, f"Safe text was refused: {text}"
            assert result.reason is None
    
    def test_dosage_patterns_refused(self):
        """Test that dosage patterns are refused."""
        dangerous_texts = [
            "Take 500mg aspirin",
            "Administer 10ml solution",
            "Give 2 tablets",
            "Prescribe 100mg medication"
        ]
        
        for text in dangerous_texts:
            result = safety_gate(text)
            assert not result.allowed, f"Dangerous text was allowed: {text}"
            assert result.reason is not None
            assert "dangerous medical advice pattern" in result.reason
    
    def test_diagnosis_claims_refused(self):
        """Test that diagnosis claims are refused."""
        dangerous_texts = [
            "You have cancer",
            "Patient has diabetes",
            "Diagnosis is heart attack",
            "Diagnosed with hypertension"
        ]
        
        for text in dangerous_texts:
            result = safety_gate(text)
            assert not result.allowed, f"Diagnosis claim was allowed: {text}"
            assert result.reason is not None
    
    def test_emergency_patterns_refused(self):
        """Test that emergency patterns are refused."""
        dangerous_texts = [
            "This is an emergency",
            "Call 911 immediately",
            "Go to ER right now",
            "Life-threatening condition"
        ]
        
        for text in dangerous_texts:
            result = safety_gate(text)
            assert not result.allowed, f"Emergency pattern was allowed: {text}"
            assert result.reason is not None
    
    def test_treatment_recommendations_refused(self):
        """Test that treatment recommendations are refused."""
        dangerous_texts = [
            "Treat with antibiotics",
            "Surgery is needed",
            "Start chemotherapy",
            "Prescribe medication"
        ]
        
        for text in dangerous_texts:
            result = safety_gate(text)
            assert not result.allowed, f"Treatment recommendation was allowed: {text}"
            assert result.reason is not None
    
    def test_overly_confident_statements_refused(self):
        """Test that overly confident medical statements are refused."""
        dangerous_texts = [
            "This is definitely serious",
            "Certainly concerning",
            "Absolutely problematic",
            "Guaranteed to be significant"
        ]
        
        for text in dangerous_texts:
            result = safety_gate(text)
            assert not result.allowed, f"Overly confident statement was allowed: {text}"
            assert result.reason is not None
            assert "overly confident medical statement" in result.reason
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Empty or whitespace
        assert safety_gate("").allowed
        assert safety_gate("   ").allowed
        assert safety_gate(None).allowed
        
        # Mixed case
        result = safety_gate("TAKE 500MG ASPIRIN")
        assert not result.allowed
        
        # Partial matches
        result = safety_gate("The patient may benefit from evaluation")
        assert result.allowed
    
    def test_safety_result_structure(self):
        """Test that SafetyResult has correct structure."""
        safe_result = safety_gate("Safe text")
        assert isinstance(safe_result, SafetyResult)
        assert safe_result.allowed is True
        assert safe_result.reason is None
        
        dangerous_result = safety_gate("Take 500mg aspirin")
        assert isinstance(dangerous_result, SafetyResult)
        assert dangerous_result.allowed is False
        assert isinstance(dangerous_result.reason, str)
        assert len(dangerous_result.reason) > 0
