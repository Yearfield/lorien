import streamlit as st
from ui_streamlit.api_client import get_json, post_file
import pandas as pd

st.set_page_config(
    page_title="Workspace - Lorien",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Workspace")
st.caption("Import Excel workbooks, export data, and monitor system health")

# Navigation
if st.button("🏠 Home", use_container_width=True):
    st.switch_page("Home.py")

# Health widget
st.header("📊 System Health")
try:
    health_data = get_json("/health")
    
    if health_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Status", "✅ Healthy" if health_data.get("status") == "ok" else "❌ Unhealthy")
            if health_data.get("version"):
                st.caption(f"Version: {health_data['version']}")
        
        with col2:
            db_status = "✅ Connected" if health_data.get("db", {}).get("foreign_keys") else "❌ Error"
            st.metric("Database", db_status)
        
        with col3:
            llm_status = "✅ Enabled" if health_data.get("features", {}).get("llm") else "❌ Disabled"
            st.metric("LLM", llm_status)
        
        # Show full health data in expander
        with st.expander("📋 Full Health Data"):
            st.json(health_data)
    else:
        st.error("❌ Could not load health data")
        
except Exception as e:
    st.error(f"❌ Health check failed: {str(e)[:100]}...")
    st.info("Please check your API connection in Settings")

# Excel Import
st.header("📥 Import Excel Workbook")
st.info("Upload an Excel file to import decision tree data")

uploaded_file = st.file_uploader(
    "Choose an Excel file",
    type=['xlsx', 'xls'],
    help="Upload .xlsx or .xls files with decision tree data"
)

if uploaded_file is not None:
    # Show file info
    st.write(f"**File:** {uploaded_file.name}")
    st.write(f"**Size:** {uploaded_file.size} bytes")
    st.write(f"**Type:** {uploaded_file.type}")
    
    # Import button with progress indicators
    if st.button("🚀 Import Excel Workbook", type="primary"):
        try:
            with st.status("📤 Queued...", expanded=False) as status:
                status.write("📤 Queued for processing...")
                
                # Prepare file for upload
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                
                status.write("🔍 Validating file format...")
                
                # Upload file
                status.write("📝 Processing Excel data...")
                result = post_file("/import/excel", files)
                
                status.write("✅ Done!")
                
                # Show results
                if result.get("ok"):
                    st.success("✅ Excel workbook imported successfully!")
                    
                    # Show summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Inserted", result.get("inserted", 0))
                    with col2:
                        st.metric("Updated", result.get("updated", 0))
                    with col3:
                        st.metric("Skipped", result.get("skipped", 0))
                    
                    # Show validation results
                    if result.get("header_validation"):
                        validation = result["header_validation"]
                        if validation.get("ok"):
                            st.success("✅ Header validation passed")
                        else:
                            st.error("❌ Header validation failed")
                            for error in validation.get("errors", []):
                                st.error(f"Position {error.get('pos')}: Expected '{error.get('expected')}', got '{error.get('got')}'")
                    
                    # Show row errors if any
                    if result.get("row_errors"):
                        st.warning("⚠️ Some rows had errors:")
                        for error in result["row_errors"]:
                            st.write(f"Row {error.get('row')}: {error.get('type')} - {error.get('count')} errors")
                    
                    # Show summary if available
                    if result.get("summary"):
                        with st.expander("📊 Import Summary"):
                            st.json(result["summary"])
                    
                    # Refresh health data after import
                    st.rerun()
                    
                else:
                    st.error("❌ Import failed")
                    st.write(result)
                    
        except Exception as e:
            st.error(f"❌ Import error: {str(e)[:100]}...")
            st.info("Please check your API connection and file format")

# Export options
st.header("📤 Export Data")

# CSV Export
st.subheader("📊 CSV Export")
col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Export Calculator Data (CSV)", use_container_width=True):
        try:
            csv_data = get_json("/calc/export")
            st.success("✅ CSV export ready")
            st.download_button(
                label="Download Calculator CSV",
                data=csv_data,
                file_name="lorien_calculator_data.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"❌ CSV export error: {str(e)[:100]}...")

with col2:
    if st.button("📊 Export All Tree Data (CSV)", use_container_width=True):
        try:
            csv_data = get_json("/tree/export")
            st.success("✅ CSV export ready")
            st.download_button(
                label="Download All Tree CSV",
                data=csv_data,
                file_name="lorien_all_tree_data.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"❌ CSV export error: {str(e)[:100]}...")

# XLSX Export
st.subheader("📊 XLSX Export")
col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Export Calculator Data (XLSX)", use_container_width=True):
        try:
            xlsx_data = get_json("/calc/export.xlsx")
            st.success("✅ XLSX export ready")
            st.download_button(
                label="Download Calculator XLSX",
                data=xlsx_data,
                file_name="lorien_calculator_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"❌ XLSX export error: {str(e)[:100]}...")

with col2:
    if st.button("📊 Export All Tree Data (XLSX)", use_container_width=True):
        try:
            xlsx_data = get_json("/tree/export.xlsx")
            st.success("✅ XLSX export ready")
            st.download_button(
                label="Download All Tree XLSX",
                data=xlsx_data,
                file_name="lorien_all_tree_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.error(f"❌ XLSX export error: {str(e)[:100]}...")

# Header preview
st.header("📋 Export Header Preview")
st.info("All exports use the following 8-column format:")
st.code("Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions")

# Statistics
st.header("📊 Data Statistics")
try:
    stats = get_json("/tree/stats")
    
    if stats:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Nodes", stats.get("nodes", 0))
        with col2:
            st.metric("Root Nodes", stats.get("roots", 0))
        with col3:
            st.metric("Leaf Nodes", stats.get("leaves", 0))
        with col4:
            st.metric("Complete Paths", stats.get("complete_paths", 0))
        
        # Show incomplete parents
        if stats.get("incomplete_parents", 0) > 0:
            st.warning(f"⚠️ {stats['incomplete_parents']} parents have incomplete child slots")
            
            if st.button("🔍 Jump to Next Incomplete Parent"):
                try:
                    next_incomplete = get_json("/tree/next-incomplete-parent")
                    if next_incomplete:
                        st.success(f"Next incomplete parent: Node {next_incomplete.get('id')} - {next_incomplete.get('label')}")
                        st.info("Use the Editor tab to complete this parent's child slots")
                    else:
                        st.info("No incomplete parents found!")
                except Exception as e:
                    st.error(f"Could not find next incomplete parent: {str(e)[:100]}...")
    else:
        st.info("📊 No statistics available")
        
except Exception as e:
    st.error(f"❌ Could not load statistics: {str(e)[:100]}...")

# Backup & Restore
st.header("💾 Backup & Restore")
st.info("Create database backups and restore from previous versions")

col1, col2 = st.columns(2)

with col1:
    if st.button("💾 Create Backup", use_container_width=True):
        try:
            with st.status("Creating backup...", expanded=False) as status:
                status.write("📤 Initiating backup...")
                
                backup_result = post_json("/backup", {})
                
                status.write("✅ Backup complete!")
                
                if backup_result.get("ok"):
                    st.success(f"✅ Backup created successfully!")
                    st.info(f"**Path:** {backup_result.get('path')}")
                    st.info(f"**Integrity:** {'✅ OK' if backup_result.get('integrity', {}).get('ok') else '❌ Failed'}")
                    
                    if backup_result.get("integrity", {}).get("details"):
                        st.info(f"**Details:** {backup_result['integrity']['details']}")
                else:
                    st.error("❌ Backup failed")
                    st.write(backup_result)
                    
        except Exception as e:
            st.error(f"❌ Backup error: {str(e)[:100]}...")

with col2:
    if st.button("🔄 Restore Latest", use_container_width=True):
        try:
            with st.status("Restoring from backup...", expanded=False) as status:
                status.write("📤 Initiating restore...")
                
                restore_result = post_json("/restore", {})
                
                status.write("✅ Restore complete!")
                
                if restore_result.get("ok"):
                    st.success(f"✅ Restore completed successfully!")
                    st.info(f"**Integrity:** {'✅ OK' if restore_result.get('integrity', {}).get('ok') else '❌ Failed'}")
                    
                    if restore_result.get("integrity", {}).get("details"):
                        st.info(f"**Details:** {restore_result['integrity']['details']}")
                        
                    st.warning("⚠️ Please refresh the page to see updated data")
                else:
                    st.error("❌ Restore failed")
                    st.write(restore_result)
                    
        except Exception as e:
            st.error(f"❌ Restore error: {str(e)[:100]}...")

# Backup Status
if st.button("📋 Show Backup Status"):
    try:
        status_data = get_json("/backup/status")
        
        if status_data:
            st.subheader("📋 Backup Status")
            
            if status_data.get("backups"):
                for backup in status_data["backups"]:
                    with st.expander(f"📁 {backup.get('filename', 'Unknown')}"):
                        st.write(f"**Size:** {backup.get('size', 'Unknown')}")
                        st.write(f"**Created:** {backup.get('created', 'Unknown')}")
                        st.write(f"**Integrity:** {'✅ OK' if backup.get('integrity', {}).get('ok') else '❌ Failed'}")
            else:
                st.info("No backups found")
        else:
            st.error("Could not load backup status")
            
    except Exception as e:
        st.error(f"❌ Could not load backup status: {str(e)[:100]}...")

# Help section
st.header("❓ Workspace Help")
st.markdown("""
**Workspace Features:**
- 📥 **Import**: Upload Excel workbooks to populate decision trees
- 📤 **Export**: Download data in CSV or XLSX formats
- 📊 **Health**: Monitor system status and database health
- 📈 **Statistics**: View data completeness and tree structure

**Import Requirements:**
- Excel files (.xlsx or .xls)
- 8-column header format (see preview above)
- Valid decision tree structure

**Export Formats:**
- **CSV**: Simple text format, good for data analysis
- **XLSX**: Excel format, preserves formatting and structure

**Quick Actions:**
1. **Import** your Excel workbook
2. **Check** system health and statistics
3. **Export** data as needed
4. **Navigate** to other pages to manage trees
""")
