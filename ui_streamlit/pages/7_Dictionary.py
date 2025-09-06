from __future__ import annotations
import streamlit as st
from ui_streamlit.api_client import get_json, post_json
import pandas as pd

st.set_page_config(
    page_title="Dictionary - Lorien",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Dictionary Management")
st.caption("Manage medical terms and import/export dictionary data")

# Navigation
col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")
with col2:
    if st.button("📝 Editor", use_container_width=True):
        st.switch_page("pages/1_Editor.py")

# Search and Filter
st.header("🔍 Search Dictionary")
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    query = st.text_input("Search terms", placeholder="e.g., fever, pain")
with col2:
    term_type = st.selectbox("Type", ["", "node_label", "vital_measurement", "outcome_template"])
with col3:
    limit = st.selectbox("Limit", [25, 50, 100], index=1)

# Search button
if st.button("🔍 Search", type="primary"):
    try:
        params = {"limit": limit}
        if query:
            params["query"] = query
        if term_type:
            params["type"] = term_type

        results = get_json("/dictionary", params=params)

        if results and "items" in results:
            items = results["items"]
            if items:
                # Display as table
                df = pd.DataFrame(items)
                st.dataframe(df, use_container_width=True)

                st.success(f"Found {len(items)} terms")
            else:
                st.info("No terms found matching your criteria")
        else:
            st.warning("No results returned")
    except Exception as e:
        st.error(f"Error searching dictionary: {str(e)[:100]}...")

# Import Section
st.header("📤 Import Dictionary Terms")
st.info("Upload a CSV or Excel file to import dictionary terms")

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["csv", "xlsx", "xls"],
    help="File should contain columns: type, term, normalized, hints, red_flag"
)

if uploaded_file is not None:
    st.write(f"**File:** {uploaded_file.name}")
    st.write(f"**Size:** {uploaded_file.size} bytes")

    # Show preview
    try:
        if uploaded_file.name.endswith('.csv'):
            df_preview = pd.read_csv(uploaded_file)
        else:
            df_preview = pd.read_excel(uploaded_file)

        st.write("**Preview (first 5 rows):**")
        st.dataframe(df_preview.head(), use_container_width=True)

        if st.button("🚀 Import Terms", type="primary"):
            try:
                # Reset file pointer
                uploaded_file.seek(0)

                # Prepare multipart data
                import requests
                from ui_streamlit.settings import get_api_base_url

                api_base = get_api_base_url()
                url = f"{api_base}/dictionary/import"

                files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                response = requests.post(url, files=files)

                if response.status_code == 200:
                    result = response.json()
                    st.success("✅ Import completed!")
                    st.json(result)
                else:
                    st.error(f"Import failed: {response.status_code}")
                    st.text(response.text[:500])

            except Exception as e:
                st.error(f"Error during import: {str(e)[:100]}...")

    except Exception as e:
        st.error(f"Error reading file: {str(e)[:100]}...")

# Bulk Operations
st.header("⚡ Bulk Operations")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Export All Terms", use_container_width=True):
        try:
            # This would need to be implemented in the API
            st.info("Export functionality would download all dictionary terms")
        except Exception as e:
            st.error(f"Error exporting: {str(e)[:100]}...")

with col2:
    if st.button("🧹 Clear All Terms", use_container_width=True, type="secondary"):
        st.warning("⚠️ This would delete all dictionary terms. Feature not implemented yet.")

# Summary
st.header("📋 Summary")
st.markdown("""
**Dictionary Management:**
- 🔍 **Search** for existing terms by type and query
- 📤 **Import** CSV/Excel files with term definitions
- 📊 **Export** terms for backup or analysis
- 🧹 **Bulk operations** for maintenance

**File Format for Import:**
- **type**: node_label, vital_measurement, outcome_template
- **term**: The actual term text
- **normalized**: Standardized version (optional)
- **hints**: Additional context (optional)
- **red_flag**: true/false (optional)
""")
