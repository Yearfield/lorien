from __future__ import annotations
import os
import streamlit as st
from ui_streamlit.components import top_health_banner
from ui_streamlit.settings import get_api_base_url

st.set_page_config(page_title="Settings", layout="wide")
st.title("Settings")

health = top_health_banner()

st.subheader("API")
st.write("Base URL resolution order: secrets.API_BASE_URL → env.API_BASE_URL → default http://localhost:8000")
st.code(get_api_base_url())

st.subheader("Environment")
st.write(f"API_BASE_URL env: {os.environ.get('API_BASE_URL')!r}")

st.info("To set a per-user override, create .streamlit/secrets.toml with:\n\nAPI_BASE_URL = \"http://127.0.0.1:8000\"")
