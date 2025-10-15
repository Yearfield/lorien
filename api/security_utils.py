"""
Security utilities for input validation and sanitization.

Provides comprehensive input validation functions for the Lorien API.
"""

import html
import re
from typing import Any, Optional

from .security import get_security_config, sanitize_input


class SecurityValidator:
    """Comprehensive input validation for security."""

    def __init__(self):
        self.config = get_security_config()

        # Patterns for various validation types
        self.patterns = {
            "sql_injection": [
                re.compile(
                    r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)",
                    re.IGNORECASE,
                ),
                re.compile(r"(\b(OR|AND)\s+\d+\s*=\s*\d+)", re.IGNORECASE),
                re.compile(r"(\b(OR|AND)\s+'.*'\s*=\s*'.*')", re.IGNORECASE),
            ],
            "xss": [
                re.compile(r"<script[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL),
                re.compile(r"javascript:", re.IGNORECASE),
                re.compile(r"vbscript:", re.IGNORECASE),
                re.compile(r"on\w+\s*=", re.IGNORECASE),  # onclick, onload, etc.
                re.compile(r"<iframe[^>]*>", re.IGNORECASE),
                re.compile(r"<object[^>]*>", re.IGNORECASE),
                re.compile(r"<embed[^>]*>", re.IGNORECASE),
            ],
            "path_traversal": [
                re.compile(r"\.\./"),
                re.compile(r"\.\.\\"),
                re.compile(r"%2e%2e%2f", re.IGNORECASE),  # URL encoded
                re.compile(r"%2e%2e%5c", re.IGNORECASE),  # URL encoded
            ],
            "command_injection": [
                re.compile(r"[;&|`$()]"),
                re.compile(r"\b(cat|ls|pwd|whoami|id|uname)\b", re.IGNORECASE),
            ],
        }

    def validate_string(self, value: Any, field_name: str = "input", max_length: int = 1000) -> str:
        """
        Validate and sanitize a string input.

        Args:
            value: Input value to validate
            field_name: Name of the field for error messages
            max_length: Maximum allowed length

        Returns:
            Sanitized string

        Raises:
            ValueError: If input is invalid
        """
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string")

        # Check length
        if len(value) > max_length:
            raise ValueError(f"{field_name} exceeds maximum length of {max_length}")

        # Check for dangerous patterns
        if not self._is_safe_input(value):
            raise ValueError(f"{field_name} contains potentially dangerous content")

        # Sanitize and return
        return sanitize_input(value)

    def validate_label(self, value: Any) -> str:
        """
        Validate a node label.

        Args:
            value: Label value to validate

        Returns:
            Validated and sanitized label

        Raises:
            ValueError: If label is invalid
        """
        label = self.validate_string(value, "label", max_length=500)

        # Additional label-specific validation
        if not label.strip():
            raise ValueError("Label cannot be empty")

        # Check for only whitespace
        if not label.strip():
            raise ValueError("Label cannot contain only whitespace")

        return label.strip()

    def validate_parent_id(self, value: Any) -> int:
        """
        Validate a parent ID.

        Args:
            value: Parent ID to validate

        Returns:
            Validated parent ID

        Raises:
            ValueError: If parent ID is invalid
        """
        try:
            parent_id = int(value)
        except (ValueError, TypeError):
            raise ValueError("Parent ID must be an integer")

        if parent_id < 0:
            raise ValueError("Parent ID must be non-negative")

        return parent_id

    def validate_depth(self, value: Any) -> int:
        """
        Validate a depth value.

        Args:
            value: Depth value to validate

        Returns:
            Validated depth

        Raises:
            ValueError: If depth is invalid
        """
        try:
            depth = int(value)
        except (ValueError, TypeError):
            raise ValueError("Depth must be an integer")

        if depth < 0 or depth > 6:
            raise ValueError("Depth must be between 0 and 6")

        return depth

    def validate_slot(self, value: Any) -> int:
        """
        Validate a slot value.

        Args:
            value: Slot value to validate

        Returns:
            Validated slot

        Raises:
            ValueError: If slot is invalid
        """
        try:
            slot = int(value)
        except (ValueError, TypeError):
            raise ValueError("Slot must be an integer")

        if slot < 1 or slot > 5:
            raise ValueError("Slot must be between 1 and 5")

        return slot

    def validate_triage_text(self, value: Any) -> Optional[str]:
        """
        Validate triage text input.

        Args:
            value: Triage text to validate

        Returns:
            Validated and sanitized triage text, or None if empty

        Raises:
            ValueError: If triage text is invalid
        """
        if value is None or value == "":
            return None

        if not isinstance(value, str):
            raise ValueError("Triage text must be a string")

        # Check length (allow longer text for triage)
        if len(value) > 5000:
            raise ValueError("Triage text exceeds maximum length of 5000 characters")

        # Check for dangerous patterns
        if not self._is_safe_input(value):
            raise ValueError("Triage text contains potentially dangerous content")

        return sanitize_input(value)

    def validate_actions_text(self, value: Any) -> Optional[str]:
        """
        Validate actions text input.

        Args:
            value: Actions text to validate

        Returns:
            Validated and sanitized actions text, or None if empty

        Raises:
            ValueError: If actions text is invalid
        """
        if value is None or value == "":
            return None

        if not isinstance(value, str):
            raise ValueError("Actions text must be a string")

        # Check length (allow longer text for actions)
        if len(value) > 5000:
            raise ValueError("Actions text exceeds maximum length of 5000 characters")

        # Check for dangerous patterns
        if not self._is_safe_input(value):
            raise ValueError("Actions text contains potentially dangerous content")

        return sanitize_input(value)

    def validate_red_flag_name(self, value: Any) -> str:
        """
        Validate a red flag name.

        Args:
            value: Red flag name to validate

        Returns:
            Validated and sanitized red flag name

        Raises:
            ValueError: If red flag name is invalid
        """
        name = self.validate_string(value, "red flag name", max_length=200)

        if not name.strip():
            raise ValueError("Red flag name cannot be empty")

        return name.strip()

    def validate_red_flag_severity(self, value: Any) -> str:
        """
        Validate a red flag severity level.

        Args:
            value: Severity level to validate

        Returns:
            Validated severity level

        Raises:
            ValueError: If severity is invalid
        """
        if not isinstance(value, str):
            raise ValueError("Severity must be a string")

        severity = value.lower().strip()
        valid_severities = {"low", "medium", "high", "critical"}

        if severity not in valid_severities:
            raise ValueError(f"Severity must be one of: {', '.join(valid_severities)}")

        return severity

    def validate_dictionary_term(self, value: Any) -> str:
        """
        Validate a dictionary term.

        Args:
            value: Dictionary term to validate

        Returns:
            Validated and sanitized dictionary term

        Raises:
            ValueError: If dictionary term is invalid
        """
        term = self.validate_string(value, "dictionary term", max_length=300)

        if not term.strip():
            raise ValueError("Dictionary term cannot be empty")

        return term.strip()

    def validate_dictionary_definition(self, value: Any) -> Optional[str]:
        """
        Validate a dictionary definition.

        Args:
            value: Dictionary definition to validate

        Returns:
            Validated and sanitized dictionary definition, or None if empty

        Raises:
            ValueError: If dictionary definition is invalid
        """
        if value is None or value == "":
            return None

        definition = self.validate_string(value, "dictionary definition", max_length=2000)

        return definition.strip() if definition.strip() else None

    def _is_safe_input(self, input_str: str) -> bool:
        """
        Check if input string is safe from various attack patterns.

        Args:
            input_str: String to check

        Returns:
            True if safe, False if potentially dangerous
        """
        if not self.config.input_validation_enabled:
            return True

        # Check all dangerous patterns
        for pattern_type, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern.search(input_str):
                    return False

        return True


# Global validator instance
validator = SecurityValidator()


def validate_request_data(data: dict[str, Any], required_fields: list[str]) -> dict[str, Any]:
    """
    Validate request data with required fields.

    Args:
        data: Request data to validate
        required_fields: List of required field names

    Returns:
        Validated data dictionary

    Raises:
        ValueError: If validation fails
    """
    if not isinstance(data, dict):
        raise ValueError("Request data must be a dictionary")

    # Check required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    return data


def sanitize_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Sanitize all string values in a dictionary.

    Args:
        data: Dictionary to sanitize

    Returns:
        Sanitized dictionary
    """
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = sanitize_input(value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_dict(value)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_input(item) if isinstance(item, str) else item for item in value
            ]
        else:
            sanitized[key] = value

    return sanitized


def escape_html(text: str) -> str:
    """
    Escape HTML characters in text.

    Args:
        text: Text to escape

    Returns:
        HTML-escaped text
    """
    return html.escape(text)


def is_safe_filename(filename: str) -> bool:
    """
    Check if filename is safe (no path traversal, etc.).

    Args:
        filename: Filename to check

    Returns:
        True if safe, False otherwise
    """
    if not filename or not isinstance(filename, str):
        return False

    # Check for path traversal patterns
    dangerous_patterns = [
        "..",
        "/",
        "\\",
        "<",
        ">",
        ":",
        '"',
        "|",
        "?",
        "*",
        "%2e%2e",
        "%2f",
        "%5c",  # URL encoded
    ]

    for pattern in dangerous_patterns:
        if pattern in filename:
            return False

    return True
