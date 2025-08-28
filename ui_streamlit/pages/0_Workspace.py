import streamlit as st
import requests
from ui_streamlit.api_client import post_file, get_csv_export, get_json

st.set_page_config(page_title="Workspace", page_icon="🏢")

st.title("🏢 Workspace")

# New Vital Measurement Creation
st.header("Create New Vital Measurement")
with st.form("new_vital_measurement"):
    vital_label = st.text_input("Vital Measurement Name", placeholder="e.g., Blood Pressure, Heart Rate")
    st.caption("Optional: Add initial child labels (up to 5)")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        child1 = st.text_input("Node 1", key="child1")
    with col2:
        child2 = st.text_input("Node 2", key="child2")
    with col3:
        child3 = st.text_input("Node 3", key="child3")
    with col4:
        child4 = st.text_input("Node 4", key="child4")
    with col5:
        child5 = st.text_input("Node 5", key="child5")
    
    submitted = st.form_submit_button("Create Vital Measurement")
    if submitted and vital_label:
        try:
            # Filter out empty children
            children = [c for c in [child1, child2, child3, child4, child5] if c.strip()]
            
            response = requests.post(
                f"{st.session_state.get('api_base', 'http://localhost:8000')}/tree/roots",
                json={"label": vital_label, "children": children}
            )
            
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ Created '{vital_label}' with {len(result['children'])} child slots!")
                st.json(result)
                
                # Deep-link to Parent Detail
                if st.button(f"Go to Editor for {vital_label}"):
                    st.session_state['selected_parent_id'] = result['root_id']
                    st.switch_page("pages/1_Editor.py")
            else:
                st.error(f"Failed to create: {response.text}")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

st.divider()

# Excel Import
st.header("📥 Import Excel Workbook")
uploaded_file = st.file_uploader("Select Excel (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    if st.button("Upload & Import"):
        try:
            data = uploaded_file.read()
            response = post_file("/import/excel", (
                uploaded_file.name, 
                data, 
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ))
            st.success("✅ Import completed successfully!")
            st.json(response)
        except Exception as e:
            st.error(f"❌ Import failed: {str(e)}")

st.divider()

# CSV Export
st.header("📤 Export Data")

# Header preview
st.subheader("CSV Header Preview")
st.code("Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions")
st.caption("The exported file starts with the 8-column canonical header")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Export Calculator (CSV)"):
        try:
            csv_content = get_csv_export("/calc/export")
            st.download_button(
                "💾 Download calculator_export.csv",
                csv_content,
                file_name="calculator_export.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Export failed: {str(e)}")
    
    if st.button("📊 Export Calculator (XLSX)"):
        try:
            response = requests.get(
                f"{st.session_state.get('api_base', 'http://localhost:8000')}/calc/export.xlsx"
            )
            if response.status_code == 200:
                st.download_button(
                    "💾 Download calculator_export.xlsx",
                    response.content,
                    file_name="calculator_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error(f"Export failed: {response.text}")
        except Exception as e:
            st.error(f"Export failed: {str(e)}")

with col2:
    if st.button("🌳 Export Tree (CSV)"):
        try:
            csv_content = get_csv_export("/tree/export")
            st.download_button(
                "💾 Download tree_export.csv",
                csv_content,
                file_name="tree_export.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Export failed: {str(e)}")
    
    if st.button("🌳 Export Tree (XLSX)"):
        try:
            response = requests.get(
                f"{st.session_state.get('api_base', 'http://localhost:8000')}/tree/export.xlsx"
            )
            if response.status_code == 200:
                st.download_button(
                    "💾 Download tree_export.xlsx",
                    response.content,
                    file_name="tree_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.error(f"Export failed: {response.text}")
        except Exception as e:
            st.error(f"Export failed: {str(e)}")

st.divider()

# Completeness Summary
st.header("📊 Completeness Summary")

if st.button("🔄 Refresh Stats"):
    try:
        stats = get_json("/tree/stats")
        st.json(stats)
        
        # Display summary cards
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Nodes", stats.get("nodes", 0))
        
        with col2:
            st.metric("Roots", stats.get("roots", 0))
        
        with col3:
            st.metric("Leaves", stats.get("leaves", 0))
        
        with col4:
            st.metric("Complete Paths", stats.get("complete_paths", 0))
        
        with col5:
            st.metric("Incomplete Parents", stats.get("incomplete_parents", 0))
        
        # Jump to next incomplete parent
        if stats.get("incomplete_parents", 0) > 0:
            if st.button("⏭️ Jump to Next Incomplete Parent"):
                try:
                    next_incomplete = get_json("/tree/next-incomplete-parent")
                    st.session_state['selected_parent_id'] = next_incomplete['parent_id']
                    st.success(f"Jumping to parent {next_incomplete['parent_id']}")
                    st.switch_page("pages/1_Editor.py")
                except Exception as e:
                    st.error(f"Jump failed: {str(e)}")
        
    except Exception as e:
        st.error(f"Failed to get stats: {str(e)}")

st.divider()

# Health Check
st.header("🏥 Health Check")
if st.button("Check API Health"):
    try:
        health = get_json("/health")
        st.json(health)
        
        # Display key metrics
        if "db_path" in health:
            st.info(f"Database: {health['db_path']}")
        if "version" in health:
            st.success(f"Version: {health['version']}")
            
    except Exception as e:
        st.error(f"Health check failed: {str(e)}")
