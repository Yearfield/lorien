from __future__ import annotations
import os
from functools import lru_cache
import streamlit as st

DEFAULT_API_BASE = "http://localhost:8000/api/v1"

@lru_cache(maxsize=1)
def get_api_base_url() -> str:
    # Priority: secrets → env → default
    base = None
    try:
        base = st.secrets.get("API_BASE_URL")  # type: ignore[attr-defined]
    except Exception:
        base = None
    if not base:
        base = os.environ.get("API_BASE_URL", DEFAULT_API_BASE)
    return base.rstrip("/")

def put_health_banner(health: dict | None) -> None:
    if not health:
        st.warning("API health unknown")
        return
    ok = health.get("ok")
    version = health.get("version", "?")
    if ok:
        st.success(f"API OK · v{version}")
    else:
        st.error(f"API UNHEALTHY · v{version}")
