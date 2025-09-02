"""
Null LLM Provider - Ready/no-op implementation for testing and development.
"""

from typing import Dict, Any


class NullProvider:
    """
    Null provider that always reports ready status.
    Used for testing, development, and as a fallback when no LLM is configured.
    """

    name = "null"

    def __init__(self, model: str | None = None):
        """
        Initialize null provider.

        Args:
            model: Model identifier (defaults to "none")
        """
        self.model = model or "none"

    def health(self) -> Dict[str, Any]:
        """
        Return health status - always reports ready.

        Returns:
            Dict with ok=True and provider information
        """
        return {
            "ok": True,
            "provider": self.name,
            "model": self.model
        }

    def suggest(self, prompt: str) -> Dict[str, str]:
        """
        Generate deterministic stub suggestions for testing.

        Args:
            prompt: The prompt text (ignored for null provider)

        Returns:
            Dict with diagnostic_triage and actions
        """
        # Basic deterministic stub for tests/dev
        return {
            "diagnostic_triage": "Acute appendicitis",
            "actions": "Immediate surgical referral"
        }
