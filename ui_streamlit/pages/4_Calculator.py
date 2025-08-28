from __future__ import annotations
import streamlit as st
import requests
from ui_streamlit.components import top_health_banner, error_message
from ui_streamlit.api_client import calc_export_csv
from ui_streamlit.settings import get_api_base_url

st.set_page_config(page_title="Calculator", layout="wide")
st.title("Calculator — Export CSV")
top_health_banner()

st.caption("Canonical headers only. Preview first line before download.")

# Path parameters input
params = st.text_input(
    "Path params (e.g. vm=DX&n1=A&n2=B&n3=C&n4=D&n5=E)", 
    value="",
    placeholder="Optional query parameters"
)

col1, col2 = st.columns(2)

# Header preview
if col1.button("Preview Header"):
    try:
        base = get_api_base_url()
        url = f"{base}/calc/export"
        if params:
            url += f"?{params}"
        
        r = requests.get(url, stream=True, timeout=10)
        if r.status_code == 200:
            first_line = next(r.iter_lines(decode_unicode=True))
            st.code(first_line)
            st.success("Header preview loaded")
        else:
            st.error(f"Export failed: {r.text}")
    except Exception as e:
        error_message(e)

# CSV download
if col2.button("Download CSV"):
    try:
        filename, data = calc_export_csv()
        st.download_button(
            "Save CSV", 
            data=data, 
            file_name=filename, 
            mime="text/csv"
        )
        st.success(f"Generated {filename}")
    except Exception as e:
        error_message(e)

# Show canonical headers info
st.info("""
**Canonical CSV Headers (8-Column Frozen Contract):**
- Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions

The header format is fixed and cannot be modified by the UI.
""")
