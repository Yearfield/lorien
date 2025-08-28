from __future__ import annotations
import streamlit as st
from ui_streamlit.components import top_health_banner, error_message
from ui_streamlit.api_client import post_file

st.set_page_config(page_title="Import", layout="wide")
st.title("Import — Excel Workbook")
st.caption("Adapter does not parse Excel; it POSTs to API importer.")

top_health_banner()

# File upload widget
uploaded_file = st.file_uploader(
    "Select Excel (.xlsx) file", 
    type=["xlsx"],
    help="Upload an Excel workbook for import"
)

if uploaded_file is not None:
    st.success(f"File selected: {uploaded_file.name}")
    st.info(f"File size: {uploaded_file.size} bytes")
    
    # Import button
    if st.button("Upload & Import", type="primary"):
        try:
            # Read file data
            file_data = uploaded_file.read()
            
            # Prepare file tuple for API client
            file_tuple = (
                uploaded_file.name,
                file_data,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
            # POST to API importer
            with st.spinner("Uploading to API..."):
                response = post_file("/import/excel", file_tuple)
            
            st.success("Import queued/processed successfully!")
            st.json(response)
            
        except Exception as e:
            error_message(e)
            st.error("Import failed. Please check the API connection and try again.")

# Import information
st.subheader("Import Process")
st.markdown("""
**How it works:**
1. **Select Excel file** - Choose a .xlsx workbook from your device
2. **Upload to API** - File is sent to the API importer endpoint
3. **API Processing** - The API handles Excel parsing and data import
4. **Response** - API returns import status and results

**Requirements:**
- File must be in .xlsx format
- API server must be running and accessible
- File size should be reasonable (typically < 10MB)

**Note:** This Streamlit adapter does not parse Excel files directly.
All processing is handled by the API to maintain the API-only architecture.
""")

# Troubleshooting
st.subheader("Troubleshooting")
if st.button("Check API Connection"):
    try:
        from ui_streamlit.api_client import get_health
        health = get_health()
        st.success("✅ API connection successful")
        st.json(health)
    except Exception as e:
        st.error("❌ API connection failed")
        st.error(str(e))
