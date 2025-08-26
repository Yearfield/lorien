#!/usr/bin/env python3
"""
Streamlit Adapter for Decision Tree Manager

This is a DEVELOPMENT adapter for quick demos and testing.
Production UIs are Flutter/Kivy.

Uses only core/services or FastAPI API calls - no direct DB or Google Sheets access.
"""

from __future__ import annotations
import streamlit as st
from .components import top_health_banner

st.set_page_config(page_title="Lorien (Streamlit adapter)", layout="wide", initial_sidebar_state="expanded")

st.title("Lorien — Streamlit Adapter")
st.write("This UI is a thin adapter over the Lorien API. For full UX, use the Flutter app.")

health = top_health_banner()

st.markdown("### Quick Navigation")
st.page_link("pages/1_Editor.py", label="Editor")
st.page_link("pages/2_Parent_Detail.py", label="Parent Detail")
st.page_link("pages/3_Flags.py", label="Flags")
st.page_link("pages/4_Calculator.py", label="Calculator")
st.page_link("pages/5_Settings.py", label="Settings")
