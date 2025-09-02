"""
LLM Provider Interface Protocol
"""

from typing import Protocol, Dict, Any


class LLMProvider(Protocol):
    """
    Protocol for LLM providers.
    All providers must implement this interface.
    """

    @property
    def name(self) -> str:
        """Provider name identifier."""
        ...

    def health(self) -> Dict[str, Any]:
        """
        Return health status without side effects.

        Returns:
            Dict with keys: ok (bool), provider (str), model (str), **meta
        """
        ...

    def suggest(self, prompt: str) -> Dict[str, str]:
        """
        Generate suggestions for diagnostic triage and actions.

        Args:
            prompt: The prompt text to generate suggestions for

        Returns:
            Dict with keys: diagnostic_triage (str), actions (str)
            Note: No normalization is applied here - that's handled upstream
        """
        ...
