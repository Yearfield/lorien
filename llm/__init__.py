"""
Local LLM integration for medical triage assistance.

This package provides optional local LLM integration for filling
diagnostic triage and actions fields from symptom paths.

The LLM is OFF by default and must be explicitly enabled via
LLM_ENABLED=true environment variable.
"""

from .config import load_llm_config, LLMConfig
from .safety import safety_gate, SafetyResult
from .json_utils import extract_first_json, parse_fill_response, clamp
from .runner import fill_triage_actions

__all__ = [
    "load_llm_config",
    "LLMConfig", 
    "safety_gate",
    "SafetyResult",
    "extract_first_json",
    "parse_fill_response",
    "clamp",
    "fill_triage_actions"
]
