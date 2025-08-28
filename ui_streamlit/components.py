from __future__ import annotations
import streamlit as st
from ui_streamlit.api_client import get_health

def top_health_banner():
    try:
        health = get_health()
        ok = health.get("ok", False)
        version = health.get("version", "?")
        if ok:
            st.sidebar.success(f"API OK · v{version}")
        else:
            st.sidebar.error(f"API UNHEALTHY · v{version}")
        return health
    except Exception as e:
        st.sidebar.error(f"API health check failed: {e}")
        return None

def error_message(e: Exception):
    st.error(f"Operation failed: {e}")
