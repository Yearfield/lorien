from __future__ import annotations
import streamlit as st
from ui_streamlit.components import top_health_banner, error_message
from ui_streamlit.api_client import flags_search, flags_assign

st.set_page_config(page_title="Flags", layout="wide")
st.title("Red Flags")
top_health_banner()

node_id = st.number_input("Node ID", min_value=1, step=1, value=1)
q = st.text_input("Search flags")
if q:
    try:
        results = flags_search(q)
        for r in results:
            with st.container():
                st.write(f"{r.get('name')}")
                if st.button(f"Assign to node {node_id}", key=f"assign_{r.get('name')}"):
                    try:
                        flags_assign(node_id, r.get("name", ""))
                        st.success("Assigned")
                    except Exception as e:
                        error_message(e)
    except Exception as e:
        error_message(e)
