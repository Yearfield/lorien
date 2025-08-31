from __future__ import annotations
import streamlit as st
import requests
from ui_streamlit.components import top_health_banner, error_message
from ui_streamlit.api_client import get_json, get_csv_export

st.set_page_config(
    page_title="Calculator - Lorien",
    page_icon="🧮",
    layout="wide"
)

st.title("🧮 Decision Tree Calculator")
st.caption("Navigate decision trees and calculate outcomes")

# Navigation
if st.button("🏠 Home", use_container_width=True):
    st.switch_page("Home.py")

# Get roots for calculator
try:
    roots = get_json("/tree/roots")
    
    if not roots:
        st.info("🌱 No decision trees found — Import a workbook in **Workspace** or create a new **Vital Measurement**.")
        st.markdown("""
        **To get started:**
        1. Go to **Workspace** and import an Excel workbook
        2. Or use **Editor** to create a new Vital Measurement
        3. Return here to calculate decision paths
        """)
        st.stop()
    
    # Calculate remaining leaves for helper text
    remaining = len(roots)
    st.session_state["remaining_leaves_count"] = remaining
    
    st.caption(f"📊 Remaining leaf options: {remaining}")
    
    # Root selection
    selected_root = st.selectbox(
        "Select Root (Vital Measurement)",
        options=roots,
        format_func=lambda x: f"{x.get('label', 'No label')} (ID: {x.get('id', 'Unknown')})"
    )
    
    if selected_root:
        root_id = selected_root.get('id')
        
        # Get children for selected root
        try:
            children = get_json(f"/tree/{root_id}/children")
            
            if children:
                # Calculate remaining leaves after root selection
                remaining = len(children)
                st.session_state["remaining_leaves_count"] = remaining
                st.caption(f"📊 Remaining leaf options: {remaining}")
                
                # Display children
                st.subheader(f"Children of {selected_root.get('label', 'Root')}")
                
                for child in children:
                    with st.expander(f"Slot {child.get('slot', 'Unknown')}: {child.get('label', 'No label')}"):
                        st.write(f"**Node ID:** {child.get('id', 'Unknown')}")
                        st.write(f"**Type:** {child.get('type', 'Unknown')}")
                        
                        # Check if this is a leaf (no children)
                        try:
                            child_children = get_json(f"/tree/{child['id']}/children")
                            if not child_children:
                                st.success("🍃 This is a leaf node")
                                
                                # Get triage information if available
                                try:
                                    triage = get_json(f"/triage/{child['id']}")
                                    if triage:
                                        st.write("**Diagnostic Triage:**")
                                        st.write(triage.get('triage', 'No triage data'))
                                        st.write("**Actions:**")
                                        st.write(triage.get('actions', 'No actions data'))
                                except:
                                    st.info("No triage data available for this leaf")
                            else:
                                st.info(f"📚 This node has {len(child_children)} children")
                        except:
                            st.info("Could not determine if this is a leaf node")
            else:
                st.info("📚 This root has no children yet")
                st.markdown("""
                **To add children:**
                1. Go to **Editor** to manage this root's children
                2. Ensure exactly 5 children are created
                3. Return here to calculate paths
                """)
                
        except Exception as e:
            st.error(f"Error loading children: {str(e)[:100]}...")
    
    # Export options
    if roots and selected_root:
        st.header("📤 Export Options")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export This Path (CSV)", use_container_width=True):
                try:
                    # Get CSV export for this specific path
                    csv_data = get_json(f"/calc/export?root_id={root_id}")
                    st.success("CSV export ready")
                    st.download_button(
                        label="Download CSV",
                        data=csv_data,
                        file_name=f"path_{root_id}.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Error exporting CSV: {str(e)[:100]}...")
        
        with col2:
            if st.button("📊 Export This Path (XLSX)", use_container_width=True):
                try:
                    # Get XLSX export for this specific path
                    xlsx_data = get_json(f"/calc/export.xlsx?root_id={root_id}")
                    st.success("XLSX export ready")
                    st.download_button(
                        label="Download XLSX",
                        data=xlsx_data,
                        file_name=f"path_{root_id}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Error exporting XLSX: {str(e)[:100]}...")
    
    # All data export
    if roots:
        st.header("📤 Export All Data")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Export All (CSV)", use_container_width=True):
                try:
                    csv_data = get_json("/tree/export")
                    st.success("All data CSV export ready")
                    st.download_button(
                        label="Download All CSV",
                        data=csv_data,
                        file_name="lorien_all_data.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Error exporting all CSV: {str(e)[:100]}...")
        
        with col2:
            if st.button("📊 Export All (XLSX)", use_container_width=True):
                try:
                    xlsx_data = get_json("/tree/export.xlsx")
                    st.success("All data XLSX export ready")
                    st.download_button(
                        label="Download All XLSX",
                        data=xlsx_data,
                        file_name="lorien_all_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Error exporting all XLSX: {str(e)[:100]}...")
    
except Exception as e:
    st.error(f"Error loading calculator data: {str(e)[:100]}...")
    st.info("Please check your API connection in Settings")

# Help section
st.header("❓ Calculator Help")
st.markdown("""
**How to use the Calculator:**
1. **Select a Root** from the dropdown above
2. **View Children** to see the decision tree structure
3. **Navigate to Leaves** to see final outcomes
4. **Export Paths** for specific decision trees
5. **Export All Data** for complete datasets

**Leaf Nodes:**
- 🍃 Leaf nodes have no children
- They contain the final diagnostic triage and actions
- Use these for decision-making and patient care

**Export Formats:**
- **CSV**: Simple text format, good for data analysis
- **XLSX**: Excel format, preserves formatting and structure
""")
