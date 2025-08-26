from __future__ import annotations
import re
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class SafetyResult:
    allowed: bool
    reason: str | None = None

# Patterns that indicate medical advice that should be refused
DANGEROUS_PATTERNS = [
    # Dosing/prescription patterns
    r'\b\d+\s*(mg|g|ml|mcg|units?)\b',  # Specific dosages
    r'\b(take|give|administer|prescribe|dosage|dose)\b',
    r'\b(aspirin|ibuprofen|acetaminophen|tylenol|advil|motrin)\b',
    
    # Diagnosis claims
    r'\b(you have|patient has|diagnosis is|diagnosed with)\b',
    r'\b(cancer|tumor|heart attack|stroke|diabetes|hypertension)\b',
    
    # Urgent/emergency patterns
    r'\b(emergency|urgent|immediate|call 911|go to ER)\b',
    r'\b(severe|critical|life-threatening|dangerous)\b',
    
    # Treatment recommendations
    r'\b(treat with|therapy|medication|drug|antibiotic)\b',
    r'\b(surgery|operation|procedure|intervention|chemotherapy)\b',
    r'\b(start|begin|initiate)\s+(treatment|therapy|medication|drug|antibiotic|chemotherapy)\b'
]

# Compile patterns for efficiency
COMPILED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in DANGEROUS_PATTERNS]

def safety_gate(text: str) -> SafetyResult:
    """
    Safety gate that refuses dangerous medical advice patterns.
    
    Args:
        text: Input text to check for safety
        
    Returns:
        SafetyResult with allowed status and reason if refused
    """
    if not text or not text.strip():
        return SafetyResult(allowed=True)
    
    text_lower = text.lower().strip()
    
    # Check for dangerous patterns
    for pattern in COMPILED_PATTERNS:
        if pattern.search(text_lower):
            return SafetyResult(
                allowed=False,
                reason=f"Content contains potentially dangerous medical advice pattern: {pattern.pattern}"
            )
    
    # Check for overly confident medical statements
    confidence_indicators = [
        "definitely", "certainly", "absolutely", "without doubt",
        "guaranteed", "proven", "scientific fact"
    ]
    
    for indicator in confidence_indicators:
        if indicator in text_lower:
            return SafetyResult(
                allowed=False,
                reason=f"Content contains overly confident medical statement: '{indicator}'"
            )
    
    return SafetyResult(allowed=True)
