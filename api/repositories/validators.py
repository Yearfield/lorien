"""
Central validators for data quality governance.

This module provides a single source of truth for normalization and validation
across the entire application, ensuring consistent data quality standards.
"""

import re
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from pydantic import ValidationError

# Allowed characters for labels (alphanumeric, spaces, hyphens, underscores, parentheses)
LABEL_ALLOWED_CHARS = re.compile(r'^[a-zA-Z0-9\s\-_()]+$')

# Prohibited tokens for outcomes (dosing/route/time tokens)
PROHIBITED_OUTCOME_TOKENS = {
    'mg', 'ml', 'mcg', 'units', 'iu', 'tablet', 'capsule', 'syringe',
    'oral', 'iv', 'im', 'subq', 'topical', 'inhaled', 'rectal',
    'daily', 'bid', 'tid', 'qid', 'prn', 'stat', 'hourly', 'weekly'
}

def normalize_label(label: str) -> str:
    """
    Normalize a label string for consistent storage.
    
    Args:
        label: Raw label string
        
    Returns:
        Normalized label string
        
    Rules:
        - Trim whitespace
        - Collapse multiple spaces to single space
        - Remove leading/trailing spaces
        - Convert to title case for consistency
    """
    if not label:
        return ""
    
    # Trim and collapse spaces
    normalized = ' '.join(label.strip().split())
    
    # Convert to title case for consistency
    normalized = normalized.title()
    
    return normalized

def validate_label(label: str, field_name: str = "label") -> str:
    """
    Validate a label string and raise 422 error if invalid.
    
    Args:
        label: Label string to validate
        field_name: Name of the field for error reporting
        
    Returns:
        Normalized label string
        
    Raises:
        HTTPException: 422 with detail[].loc/type/msg structure
    """
    if not label:
        raise HTTPException(
            status_code=422,
            detail=[{
                "loc": ["body", field_name],
                "msg": "field required",
                "type": "value_error.missing"
            }]
        )
    
    # Check length
    if len(label) > 100:
        raise HTTPException(
            status_code=422,
            detail=[{
                "loc": ["body", field_name],
                "msg": "ensure this value has at most 100 characters",
                "type": "value_error.any_str.max_length",
                "ctx": {"limit_value": 100}
            }]
        )
    
    # Check allowed characters
    if not LABEL_ALLOWED_CHARS.match(label):
        raise HTTPException(
            status_code=422,
            detail=[{
                "loc": ["body", field_name],
                "msg": "label contains invalid characters. Only letters, numbers, spaces, hyphens, underscores, and parentheses are allowed",
                "type": "value_error.invalid_chars"
            }]
        )
    
    # Normalize and return
    return normalize_label(label)

def validate_outcome_text(outcome: str, field_name: str = "outcome") -> str:
    """
    Validate outcome text and ensure it meets quality standards.
    
    Args:
        outcome: Outcome text to validate
        field_name: Name of the field for error reporting
        
    Returns:
        Normalized outcome text
        
    Raises:
        HTTPException: 422 with detail[].loc/type/msg structure
    """
    if not outcome:
        raise HTTPException(
            status_code=422,
            detail=[{
                "loc": ["body", field_name],
                "msg": "field required",
                "type": "value_error.missing"
            }]
        )
    
    # Check length (≤7 words as per requirements)
    words = outcome.split()
    if len(words) > 7:
        raise HTTPException(
            status_code=422,
            detail=[{
                "loc": ["body", field_name],
                "msg": "outcome must be 7 words or fewer",
                "type": "value_error.outcome_too_long",
                "ctx": {"word_count": len(words), "max_words": 7}
            }]
        )
    
    # Check for prohibited tokens
    outcome_lower = outcome.lower()
    prohibited_found = []
    for token in PROHIBITED_OUTCOME_TOKENS:
        if token in outcome_lower:
            prohibited_found.append(token)
    
    if prohibited_found:
        raise HTTPException(
            status_code=422,
            detail=[{
                "loc": ["body", field_name],
                "msg": f"outcome contains prohibited tokens: {', '.join(prohibited_found)}. Outcomes are guidance-only and cannot contain dosing, route, or timing information",
                "type": "value_error.prohibited_tokens",
                "ctx": {"prohibited_tokens": prohibited_found}
            }]
        )
    
    # Normalize and return
    return normalize_label(outcome)

def validate_dictionary_term(term_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate dictionary term data.
    
    Args:
        term_data: Dictionary term data to validate
        
    Returns:
        Validated and normalized term data
        
    Raises:
        HTTPException: 422 with detail[].loc/type/msg structure
    """
    validated_data = {}
    
    # Validate label
    if 'label' in term_data:
        validated_data['label'] = validate_label(term_data['label'], 'label')
    
    # Validate category
    if 'category' in term_data:
        category = term_data['category']
        if not category:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "loc": ["body", "category"],
                    "msg": "field required",
                    "type": "value_error.missing"
                }]
            )
        
        if len(category) > 50:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "loc": ["body", "category"],
                    "msg": "ensure this value has at most 50 characters",
                    "type": "value_error.any_str.max_length",
                    "ctx": {"limit_value": 50}
                }]
            )
        
        validated_data['category'] = normalize_label(category)
    
    # Validate code
    if 'code' in term_data:
        code = term_data['code']
        if code and len(code) > 20:
            raise HTTPException(
                status_code=422,
                detail=[{
                    "loc": ["body", "code"],
                    "msg": "ensure this value has at most 20 characters",
                    "type": "value_error.any_str.max_length",
                    "ctx": {"limit_value": 20}
                }]
            )
        validated_data['code'] = code
    
    return validated_data

def validate_children_data(children_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Validate children data for upsert operations.
    
    Args:
        children_data: List of children data to validate
        
    Returns:
        Validated and normalized children data
        
    Raises:
        HTTPException: 422 with detail[].loc/type/msg structure
    """
    if not children_data:
        raise HTTPException(
            status_code=422,
            detail=[{
                "loc": ["body"],
                "msg": "children data is required",
                "type": "value_error.missing"
            }]
        )
    
    validated_children = []
    
    for i, child in enumerate(children_data):
        validated_child = {}
        
        # Validate label
        if 'label' in child:
            validated_child['label'] = validate_label(child['label'], f'children[{i}].label')
        
        # Validate slot
        if 'slot' in child:
            slot = child['slot']
            if not isinstance(slot, int) or slot < 1 or slot > 5:
                raise HTTPException(
                    status_code=422,
                    detail=[{
                        "loc": ["body", f"children[{i}].slot"],
                        "msg": "slot must be an integer between 1 and 5",
                        "type": "value_error.invalid_slot",
                        "ctx": {"min_value": 1, "max_value": 5}
                    }]
                )
            validated_child['slot'] = slot
        
        # Validate depth
        if 'depth' in child:
            depth = child['depth']
            if not isinstance(depth, int) or depth < 0:
                raise HTTPException(
                    status_code=422,
                    detail=[{
                        "loc": ["body", f"children[{i}].depth"],
                        "msg": "depth must be a non-negative integer",
                        "type": "value_error.invalid_depth"
                    }]
                )
            validated_child['depth'] = depth
        
        validated_children.append(validated_child)
    
    return validated_children

def ensure_unique_5(labels: List[str]) -> List[str]:
    """
    Ensure exactly 5 unique, non-empty labels for children.
    
    Args:
        labels: List of label strings
        
    Returns:
        List of exactly 5 unique, trimmed labels
        
    Raises:
        ValueError: If not exactly 5 unique labels after filtering
    """
    if not labels:
        raise ValueError("must_choose_five")
    
    # Filter out empty strings and trim whitespace
    filtered = [label.strip() for label in labels if label.strip()]
    
    # Check for exactly 5 labels
    if len(filtered) != 5:
        raise ValueError("must_choose_five")
    
    # Check for duplicates
    if len(set(filtered)) != 5:
        raise ValueError("duplicate_labels")
    
    return filtered

def get_validation_rules() -> Dict[str, Any]:
    """
    Get current validation rules for documentation/debugging.
    
    Returns:
        Dictionary of validation rules
    """
    return {
        "label_rules": {
            "max_length": 100,
            "allowed_chars": "letters, numbers, spaces, hyphens, underscores, parentheses",
            "normalization": "trim, collapse spaces, title case"
        },
        "outcome_rules": {
            "max_words": 7,
            "prohibited_tokens": list(PROHIBITED_OUTCOME_TOKENS),
            "purpose": "guidance-only, no dosing/route/timing"
        },
        "dictionary_rules": {
            "label_max_length": 100,
            "category_max_length": 50,
            "code_max_length": 20
        },
        "children_rules": {
            "slot_range": [1, 5],
            "depth_min": 0,
            "required_fields": ["label", "slot"]
        },
        "unique_5_rules": {
            "exact_count": 5,
            "no_duplicates": True,
            "no_empty": True,
            "trim_whitespace": True
        }
    }