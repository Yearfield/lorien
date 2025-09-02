"""
LLM Service with Dependency Injection and Health Checking
"""

import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Tuple, Dict, Any
import logging

from .providers.null_provider import NullProvider

log = logging.getLogger(__name__)


def _env_bool(key: str, default: str = "false") -> bool:
    """Parse boolean environment variable."""
    return os.getenv(key, default).lower() == "true"


def _checked_at() -> str:
    """Return ISO-8601 UTC timestamp with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def resolve_provider(name: str, model: str | None = None):
    """
    Resolve provider by name.

    Args:
        name: Provider name (case-insensitive)
        model: Optional model path/identifier

    Returns:
        LLMProvider instance
    """
    name = (name or "null").lower()
    if name == "null":
        return NullProvider(model=model)
    # Future: other providers (ollama, gguf, etc.)
    return NullProvider(model=model)


class LLMService:
    """
    Tiny facade to make health deterministic & testable.
    Handles provider resolution and health checking.
    """

    def __init__(self):
        """Initialize service with environment configuration."""
        self.enabled = _env_bool("LLM_ENABLED", "false")
        self.provider_name = os.getenv("LLM_PROVIDER", "null")
        self.model_path = os.getenv("LLM_MODEL_PATH", "")
        self.provider = resolve_provider(self.provider_name, model=self.model_path or None)

    def health(self) -> Tuple[int, Dict[str, Any]]:
        """
        Check LLM service health.

        Returns:
            Tuple of (status_code, response_body)
        """
        checks = []
        try:
            if not self.enabled:
                return 503, {
                    "ok": False,
                    "llm_enabled": False,
                    "ready": False,
                    "checks": checks,
                    "checked_at": _checked_at()
                }

            # Optional file presence check
            if self.model_path:
                exists = Path(self.model_path).exists()
                checks.append({
                    "name": "model_path",
                    "ok": bool(exists),
                    "details": self.model_path if exists else "not found"
                })
                if not exists:
                    return 503, {
                        "ok": False,
                        "llm_enabled": True,
                        "ready": False,
                        "provider": self.provider_name,
                        "model": self.model_path,
                        "checks": checks,
                        "checked_at": _checked_at()
                    }

            prov = self.provider.health() or {}
            ready = bool(prov.get("ok"))
            checks.append({
                "name": "provider",
                "ok": ready,
                "details": prov
            })

            status = 200 if ready else 503
            body = {
                "ok": ready,
                "llm_enabled": True,
                "ready": ready,
                "provider": prov.get("provider", self.provider_name),
                "model": prov.get("model", self.model_path),
                "checks": checks,
                "checked_at": _checked_at()
            }
            return status, body

        except Exception:
            log.exception("LLM health error")
            return 500, {
                "ok": False,
                "error": "internal",
                "checked_at": _checked_at()
            }

    def suggest(self, prompt: str) -> Dict[str, str]:
        """
        Generate suggestions via provider.

        Args:
            prompt: The prompt text

        Returns:
            Dict with diagnostic_triage and actions (no normalization applied)
        """
        return self.provider.suggest(prompt)
