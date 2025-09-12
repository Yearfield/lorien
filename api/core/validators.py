"""
Centralized validation functions for consistent 422 error handling.

Provides single source of truth for validation logic across all write endpoints.
"""

import re
from typing import List, Dict, Any

# Word validation regex - alphanumeric, comma, hyphen, space only
WORD_REGEX = re.compile(r"^[A-Za-z0-9 ,\-]+$")

# Prohibited medical terms that should not be used in outcomes
PROHIBITED_TERMS = {
    "mg", "ml", "mcg", "g", "kg",  # Dosage units
    "iv", "im", "po", "sc", "pr",  # Administration routes
    "q6h", "q8h", "qid", "tid", "bid", "od", "qod", "prn", "stat"  # Frequency terms
}

def ensure_short_phrase(value: str, field: str, max_words: int = 7) -> str:
    """
    Validate and normalize a short phrase for outcomes.
    
    Args:
        value: The phrase to validate
        field: Field name for error messages
        max_words: Maximum number of words allowed
        
    Returns:
        Normalized phrase
        
    Raises:
        ValueError: If validation fails with detailed error message
    """
    if not value:
        raise ValueError(f"{field} cannot be empty")
    
    # Normalize whitespace
    normalized = " ".join(value.strip().split())
    
    if not normalized:
        raise ValueError(f"{field} cannot be empty")
    
    # Split into words for counting
    words = [w for w in normalized.split() if w]
    
    if len(words) == 0:
        raise ValueError(f"{field} cannot be empty")
    
    if len(words) > max_words:
        raise ValueError(f"{field} must be ≤{max_words} words")
    
    # Check character validation
    if not WORD_REGEX.fullmatch(normalized):
        raise ValueError(f"{field} contains unsupported characters")
    
    # Check for prohibited terms
    for word in words:
        if word.lower() in PROHIBITED_TERMS:
            raise ValueError(f"{field} contains prohibited term '{word}'")
    
    return normalized

def ensure_label(value: str) -> str:
    """
    Validate and normalize a label for tree nodes.
    
    Args:
        value: The label to validate
        
    Returns:
        Normalized label
        
    Raises:
        ValueError: If validation fails with detailed error message
    """
    if not value:
        raise ValueError("label cannot be empty")
    
    # Normalize whitespace
    normalized = " ".join(value.strip().split())
    
    if not normalized:
        raise ValueError("label cannot be empty")
    
    # Check character validation
    if not WORD_REGEX.fullmatch(normalized):
        raise ValueError("label must be alnum/comma/hyphen/space")
    
    return normalized

def normalize_term(term: str) -> str:
    """
    Normalize a dictionary term for consistent storage.
    
    Args:
        term: The term to normalize
        
    Returns:
        Normalized term (lowercase, collapsed whitespace)
    """
    if not term:
        return ""
    
    return " ".join(term.strip().split()).lower()

def validate_dictionary_term(term: str, field: str = "term") -> str:
    """
    Validate a dictionary term.
    
    Args:
        term: The term to validate
        field: Field name for error messages
        
    Returns:
        Validated term
        
    Raises:
        ValueError: If validation fails
    """
    if not term:
        raise ValueError(f"{field} cannot be empty")
    
    normalized = normalize_term(term)
    
    if not normalized:
        raise ValueError(f"{field} cannot be empty")
    
    if len(normalized) > 64:
        raise ValueError(f"{field} must be ≤64 characters")
    
    # Check character validation
    if not WORD_REGEX.fullmatch(term.strip()):
        raise ValueError(f"{field} must be alnum/comma/hyphen/space")
    
    return normalized

def validate_outcomes_input(data: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate outcomes input data.
    
    Args:
        data: Input data dictionary
        
    Returns:
        Validated and normalized data
        
    Raises:
        ValueError: If validation fails
    """
    validated = {}
    
    # Validate diagnostic_triage
    if "diagnostic_triage" in data:
        validated["diagnostic_triage"] = ensure_short_phrase(
            data["diagnostic_triage"], 
            "Diagnostic Triage"
        )
    
    # Validate actions
    if "actions" in data:
        validated["actions"] = ensure_short_phrase(
            data["actions"], 
            "Actions"
        )
    
    return validated

def validate_children_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate children input data.
    
    Args:
        data: Input data dictionary
        
    Returns:
        Validated and normalized data
        
    Raises:
        ValueError: If validation fails
    """
    validated = {"slots": []}
    
    if "slots" not in data:
        raise ValueError("slots field is required")
    
    if not isinstance(data["slots"], list):
        raise ValueError("slots must be a list")
    
    if len(data["slots"]) == 0:
        raise ValueError("slots cannot be empty")
    
    if len(data["slots"]) > 5:
        raise ValueError("slots cannot exceed 5 items")
    
    # Validate each slot
    for i, slot in enumerate(data["slots"]):
        if not isinstance(slot, dict):
            raise ValueError(f"slot {i} must be an object")
        
        if "slot" not in slot:
            raise ValueError(f"slot {i} missing slot number")
        
        if not isinstance(slot["slot"], int):
            raise ValueError(f"slot {i} slot number must be integer")
        
        if slot["slot"] < 1 or slot["slot"] > 5:
            raise ValueError(f"slot {i} slot number must be 1-5")
        
        # Validate label (can be empty for deletion)
        if "label" in slot:
            if slot["label"]:  # Only validate non-empty labels
                slot["label"] = ensure_label(slot["label"])
            else:
                slot["label"] = ""  # Normalize empty strings
        
        validated["slots"].append(slot)
    
    return validated

def create_422_error_detail(field: str, message: str, input_value: Any = None) -> Dict[str, Any]:
    """
    Create a standardized 422 error detail object.
    
    Args:
        field: Field name that failed validation
        message: Error message
        input_value: The input value that failed (optional)
        
    Returns:
        Standardized error detail dictionary
    """
    detail = {
        "type": "value_error",
        "loc": ["body", field],
        "msg": message,
        "input": input_value
    }
    
    return detail

def validate_and_create_422_errors(validation_errors: List[ValueError]) -> List[Dict[str, Any]]:
    """
    Convert validation errors to standardized 422 error details.
    
    Args:
        validation_errors: List of ValueError exceptions
        
    Returns:
        List of standardized error detail dictionaries
    """
    errors = []
    
    for error in validation_errors:
        # Extract field name from error message if possible
        field = "unknown"
        message = str(error)
        
        # Try to extract field name from common patterns
        if "Diagnostic Triage" in message:
            field = "diagnostic_triage"
        elif "Actions" in message:
            field = "actions"
        elif "label" in message.lower():
            field = "label"
        elif "term" in message.lower():
            field = "term"
        
        errors.append(create_422_error_detail(field, message))
    
    return errors
