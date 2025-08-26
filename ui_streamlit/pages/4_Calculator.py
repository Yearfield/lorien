from __future__ import annotations
import streamlit as st
from ui_streamlit.components import top_health_banner, error_message
from ui_streamlit.api_client import calc_export_csv

st.set_page_config(page_title="Calculator", layout="wide")
st.title("Calculator Export")
top_health_banner()

if st.button("Export CSV", type="primary"):
    try:
        filename, data = calc_export_csv()
        st.download_button("Download CSV", data=data, file_name=filename, mime="text/csv")
        st.success(f"Generated {filename}")
    except Exception as e:
        error_message(e)
