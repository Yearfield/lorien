import streamlit as st
from ui_streamlit.api_client import post_file, get_json, get_csv_export

st.set_page_config(page_title="Workspace", layout="wide")

st.title("Workspace")

# Excel Import Section
st.header("Excel Import")
uploaded_file = st.file_uploader("Choose Excel file", type=['xlsx'])

if uploaded_file is not None:
    if st.button("Import Excel"):
        try:
            file_content = uploaded_file.read()
            result = post_file("/import/excel", (uploaded_file.name, file_content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"))
            
            if result.get("ok"):
                st.success("Import successful!")
                st.json({
                    "inserted": result.get("inserted", 0),
                    "updated": result.get("updated", 0),
                    "skipped": result.get("skipped", 0)
                })
                
                # Show summary
                if "summary" in result:
                    summary = result["summary"]
                    st.info(f"Total nodes: {summary.get('total_nodes', 0)}, Parents with missing slots: {summary.get('parents_missing_slots', 0)}, Leaves with outcomes: {summary.get('leaves_with_outcomes', 0)}")
            else:
                st.error("Import failed")
                if "header_validation" in result and not result["header_validation"]["ok"]:
                    st.error("Header validation failed:")
                    for error in result["header_validation"]["errors"]:
                        st.error(f"Position {error['pos']}: Expected '{error['expected']}', got '{error['got']}'")
                        
        except Exception as e:
            st.error(f"Import error: {str(e)}")

# CSV Export Section
st.header("CSV Export")
if st.button("Preview CSV Header"):
    try:
        csv_content = get_csv_export("/calc/export")
        if csv_content:
            first_line = csv_content.split('\n')[0]
            st.code(first_line, language="text")
            
            # Verify against frozen contract
            expected = "Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions"
            if first_line == expected:
                st.success("✅ Header matches frozen contract exactly")
            else:
                st.error("❌ Header mismatch detected")
                st.error(f"Expected: {expected}")
                st.error(f"Got: {first_line}")
        else:
            st.error("Failed to retrieve CSV content")
    except Exception as e:
        st.error(f"CSV preview failed: {str(e)}")

if st.button("Download CSV"):
    try:
        csv_content = get_csv_export("/calc/export")
        if csv_content:
            st.download_button(
                label="Download CSV",
                data=csv_content,
                file_name="lorien_export.csv",
                mime="text/csv"
            )
        else:
            st.error("Failed to retrieve CSV content")
    except Exception as e:
        st.error(f"CSV download failed: {str(e)}")

# Health Section
st.header("System Health")
if st.button("Check Health"):
    try:
        health_data = get_json("/health")
        st.json(health_data)
        
        # Display key metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Version", health_data.get("version", "Unknown"))
        with col2:
            st.metric("Database Path", health_data.get("db", {}).get("path", "Unknown"))
        with col3:
            st.metric("Status", health_data.get("status", "Unknown"))
            
    except Exception as e:
        st.error(f"Health check failed: {str(e)}")
