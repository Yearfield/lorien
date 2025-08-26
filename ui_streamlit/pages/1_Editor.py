from __future__ import annotations
import streamlit as st
from ui_streamlit.components import top_health_banner, error_message
from ui_streamlit.api_client import get_next_incomplete_parent

st.set_page_config(page_title="Editor", layout="wide")
st.title("Editor")

top_health_banner()

st.markdown("Use **Skip to next incomplete parent** to focus curation.")

col1, col2 = st.columns([1,1])
if col1.button("Skip to next incomplete parent", type="primary"):
    try:
        data = get_next_incomplete_parent()
        if not data:
            st.success("No incomplete parents found.")
        else:
            pid = data.get("parent_id")
            st.session_state["last_incomplete_parent"] = pid
            st.success(f"Next incomplete parent: {pid}")
            st.page_link("pages/2_Parent_Detail.py", label="Open Parent Detail", icon="➡️")
    except Exception as e:
        error_message(e)

st.info("Tip: Use the Settings page to configure API base URL if needed.")
