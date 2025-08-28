from __future__ import annotations
import streamlit as st
import requests
from ui_streamlit.components import top_health_banner, error_message
from ui_streamlit.api_client import get_json, get_csv_export

st.set_page_config(page_title="Calculator", page_icon="🧮")

st.title("🧮 Calculator")

# Initialize session state for selections
if 'selected_root_id' not in st.session_state:
    st.session_state['selected_root_id'] = None
if 'selected_n1_id' not in st.session_state:
    st.session_state['selected_n1_id'] = None
if 'selected_n2_id' not in st.session_state:
    st.session_state['selected_n2_id'] = None
if 'selected_n3_id' not in st.session_state:
    st.session_state['selected_n3_id'] = None
if 'selected_n4_id' not in st.session_state:
    st.session_state['selected_n4_id'] = None
if 'selected_n5_id' not in st.session_state:
    st.session_state['selected_n5_id'] = None

# Get roots for dropdown 1
try:
    roots = get_json("/tree/roots")
except:
    roots = []

# Dropdown 1: Roots
st.header("1️⃣ Select Root (Vital Measurement)")
if roots:
    root_options = {f"{root['label']} (ID: {root['id']})": root['id'] for root in roots}
    selected_root_label = st.selectbox(
        "Choose a root node:",
        options=list(root_options.keys()),
        index=0 if not st.session_state['selected_root_id'] else None,
        key="root_select"
    )
    
    if selected_root_label:
        st.session_state['selected_root_id'] = root_options[selected_root_label]
        # Reset deeper selections when root changes
        st.session_state['selected_n1_id'] = None
        st.session_state['selected_n2_id'] = None
        st.session_state['selected_n3_id'] = None
        st.session_state['selected_n4_id'] = None
        st.session_state['selected_n5_id'] = None
else:
    st.warning("No root nodes found. Create some in the Workspace first.")

# Dropdown 2: Children of root (Node 1)
if st.session_state['selected_root_id']:
    st.header("2️⃣ Select Node 1")
    try:
        children = get_json(f"/tree/{st.session_state['selected_root_id']}/children")
        if children:
            node1_options = {f"{child['label'] or 'Empty'} (Slot {child['slot']}, ID: {child['id']})": child['id'] 
                            for child in children if child['slot'] == 1}
            
            if node1_options:
                selected_n1_label = st.selectbox(
                    "Choose Node 1:",
                    options=list(node1_options.keys()),
                    index=0 if not st.session_state['selected_n1_id'] else None,
                    key="n1_select"
                )
                
                if selected_n1_label:
                    st.session_state['selected_n1_id'] = node1_options[selected_n1_label]
                    # Reset deeper selections
                    st.session_state['selected_n2_id'] = None
                    st.session_state['selected_n3_id'] = None
                    st.session_state['selected_n4_id'] = None
                    st.session_state['selected_n5_id'] = None
            else:
                st.info("No Node 1 found for this root")
        else:
            st.info("No children found for this root")
    except Exception as e:
        st.error(f"Failed to load Node 1 options: {str(e)}")

# Dropdown 3: Children of Node 1 (Node 2)
if st.session_state['selected_n1_id']:
    st.header("3️⃣ Select Node 2")
    try:
        children = get_json(f"/tree/{st.session_state['selected_n1_id']}/children")
        if children:
            node2_options = {f"{child['label'] or 'Empty'} (Slot {child['slot']}, ID: {child['id']})": child['id'] 
                            for child in children if child['slot'] == 2}
            
            if node2_options:
                selected_n2_label = st.selectbox(
                    "Choose Node 2:",
                    options=list(node2_options.keys()),
                    index=0 if not st.session_state['selected_n2_id'] else None,
                    key="n2_select"
                )
                
                if selected_n2_label:
                    st.session_state['selected_n2_id'] = node2_options[selected_n2_label]
                    # Reset deeper selections
                    st.session_state['selected_n3_id'] = None
                    st.session_state['selected_n4_id'] = None
                    st.session_state['selected_n5_id'] = None
            else:
                st.info("No Node 2 found")
        else:
            st.info("No children found for Node 1")
    except Exception as e:
        st.error(f"Failed to load Node 2 options: {str(e)}")

# Dropdown 4: Children of Node 2 (Node 3)
if st.session_state['selected_n2_id']:
    st.header("4️⃣ Select Node 3")
    try:
        children = get_json(f"/tree/{st.session_state['selected_n2_id']}/children")
        if children:
            node3_options = {f"{child['label'] or 'Empty'} (Slot {child['slot']}, ID: {child['id']})": child['id'] 
                            for child in children if child['slot'] == 3}
            
            if node3_options:
                selected_n3_label = st.selectbox(
                    "Choose Node 3:",
                    options=list(node3_options.keys()),
                    index=0 if not st.session_state['selected_n3_id'] else None,
                    key="n3_select"
                )
                
                if selected_n3_label:
                    st.session_state['selected_n3_id'] = node3_options[selected_n3_label]
                    # Reset deeper selections
                    st.session_state['selected_n4_id'] = None
                    st.session_state['selected_n5_id'] = None
            else:
                st.info("No Node 3 found")
        else:
            st.info("No children found for Node 2")
    except Exception as e:
        st.error(f"Failed to load Node 3 options: {str(e)}")

# Dropdown 5: Children of Node 3 (Node 4)
if st.session_state['selected_n3_id']:
    st.header("5️⃣ Select Node 4")
    try:
        children = get_json(f"/tree/{st.session_state['selected_n3_id']}/children")
        if children:
            node4_options = {f"{child['label'] or 'Empty'} (Slot {child['slot']}, ID: {child['id']})": child['id'] 
                            for child in children if child['slot'] == 4}
            
            if node4_options:
                selected_n4_label = st.selectbox(
                    "Choose Node 4:",
                    options=list(node4_options.keys()),
                    index=0 if not st.session_state['selected_n4_id'] else None,
                    key="n4_select"
                )
                
                if selected_n4_label:
                    st.session_state['selected_n4_id'] = node4_options[selected_n4_label]
                    # Reset deeper selections
                    st.session_state['selected_n5_id'] = None
            else:
                st.info("No Node 4 found")
        else:
            st.info("No children found for Node 3")
    except Exception as e:
        st.error(f"Failed to load Node 4 options: {str(e)}")

# Dropdown 6: Children of Node 4 (Node 5 - Leaf)
if st.session_state['selected_n4_id']:
    st.header("6️⃣ Select Node 5 (Leaf)")
    try:
        children = get_json(f"/tree/{st.session_state['selected_n4_id']}/children")
        if children:
            node5_options = {f"{child['label'] or 'Empty'} (Slot {child['slot']}, ID: {child['id']})": child['id'] 
                            for child in children if child['slot'] == 5}
            
            if node5_options:
                selected_n5_label = st.selectbox(
                    "Choose Node 5 (Leaf):",
                    options=list(node5_options.keys()),
                    index=0 if not st.session_state['selected_n5_id'] else None,
                    key="n5_select"
                )
                
                if selected_n5_label:
                    st.session_state['selected_n5_id'] = node5_options[selected_n5_label]
            else:
                st.info("No Node 5 found")
        else:
            st.info("No children found for Node 4")
    except Exception as e:
        st.error(f"Failed to load Node 5 options: {str(e)}")

# Display outcomes when leaf is reached
if st.session_state['selected_n5_id']:
    st.header("🎯 Outcomes at Leaf")
    
    try:
        # Get triage data for the leaf
        triage = get_json(f"/triage/{st.session_state['selected_n5_id']}")
        
        if triage:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📋 Diagnostic Triage")
                st.write(triage.get("diagnostic_triage", "Not set"))
            
            with col2:
                st.subheader("⚡ Actions")
                st.write(triage.get("actions", "Not set"))
        else:
            st.info("No triage data found for this leaf node")
            
    except Exception as e:
        st.error(f"Failed to load triage data: {str(e)}")
    
    # Export this single path
    st.header("📤 Export This Path")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Path (CSV)"):
            try:
                # Get the path data
                path_data = get_json(f"/tree/{st.session_state['selected_n5_id']}/path")
                if path_data:
                    # Create CSV content for this single path
                    csv_content = "Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions\n"
                    
                    # Build the path string
                    path_parts = []
                    if st.session_state['selected_root_id']:
                        root_info = next((r for r in roots if r['id'] == st.session_state['selected_root_id']), None)
                        path_parts.append(root_info['label'] if root_info else "Unknown")
                    
                    # Add node labels
                    for node_id in [st.session_state['selected_n1_id'], st.session_state['selected_n2_id'], 
                                  st.session_state['selected_n3_id'], st.session_state['selected_n4_id'], 
                                  st.session_state['selected_n5_id']]:
                        if node_id:
                            try:
                                node_info = get_json(f"/tree/{node_id}/info")
                                path_parts.append(node_info.get('label', 'Unknown'))
                            except:
                                path_parts.append('Unknown')
                        else:
                            path_parts.append('')
                    
                    # Pad to exactly 5 nodes
                    while len(path_parts) < 6:  # root + 5 nodes
                        path_parts.append('')
                    
                    # Add triage data
                    triage = get_json(f"/triage/{st.session_state['selected_n5_id']}")
                    diagnostic_triage = triage.get("diagnostic_triage", "") if triage else ""
                    actions = triage.get("actions", "") if triage else ""
                    
                    # Create CSV row
                    csv_row = f"{path_parts[0]},{path_parts[1]},{path_parts[2]},{path_parts[3]},{path_parts[4]},{path_parts[5]},{diagnostic_triage},{actions}"
                    csv_content += csv_row
                    
                    st.download_button(
                        "💾 Download path_export.csv",
                        csv_content,
                        file_name="path_export.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("Failed to get path data")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")
    
    with col2:
        if st.button("📊 Export Path (XLSX)"):
            try:
                response = requests.get(
                    f"{st.session_state.get('api_base', 'http://localhost:8000')}/calc/export.xlsx"
                )
                if response.status_code == 200:
                    st.download_button(
                        "💾 Download path_export.xlsx",
                        response.content,
                        file_name="path_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.error(f"Export failed: {response.text}")
            except Exception as e:
                st.error(f"Export failed: {str(e)}")

# CSV Header Preview
st.divider()
st.header("📋 CSV Header Contract")
st.code("Vital Measurement,Node 1,Node 2,Node 3,Node 4,Node 5,Diagnostic Triage,Actions")
st.caption("The exported file starts with the exact 8-column canonical header")

# Export all data
st.divider()
st.header("📤 Export All Data")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Export All (CSV)"):
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

with col2:
    if st.button("📊 Export All (XLSX)"):
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
