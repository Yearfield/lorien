import streamlit as st
import requests
from ui_streamlit.api_client import get_json

st.set_page_config(page_title="Conflicts", page_icon="⚠️")

st.title("⚠️ Conflicts & Validation")

# Validation Options Panel
st.header("🔍 Validation Options")
with st.expander("Validation Options", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        check_duplicates = st.checkbox("Duplicate Labels", value=False, help="Show nodes with duplicate labels under same parent")
    
    with col2:
        check_orphans = st.checkbox("Orphan Nodes", value=False, help="Show nodes with invalid parent references")
    
    with col3:
        check_depth = st.checkbox("Depth Anomalies", value=False, help="Show nodes with invalid depth values")

# Pagination controls
col1, col2, col3 = st.columns(3)
with col1:
    page_size = st.selectbox("Page Size", [25, 50, 100, 200], index=2)
with col2:
    page_number = st.number_input("Page", min_value=0, value=0, step=1)
with col3:
    offset = page_number * page_size

# Search/filter
search_query = st.text_input("🔍 Search by label or parent ID", placeholder="e.g., 'High' or '123'")

# Duplicate Labels Validation
if check_duplicates:
    st.header("🚨 Duplicate Labels")
    
    try:
        duplicates = get_json(f"/tree/conflicts/duplicate-labels?limit={page_size}&offset={offset}")
        
        if duplicates:
            # Filter by search query if provided
            if search_query:
                filtered_duplicates = []
                for dup in duplicates:
                    if (search_query.lower() in dup.get('label', '').lower() or 
                        search_query.lower() in dup.get('parent_label', '').lower() or
                        search_query in str(dup.get('parent_id', ''))):
                        filtered_duplicates.append(dup)
                duplicates = filtered_duplicates
            
            if filtered_duplicates:
                st.success(f"Found {len(filtered_duplicates)} duplicate label conflicts")
                
                for dup in filtered_duplicates:
                    with st.expander(f"🚨 '{dup['label']}' under '{dup['parent_label']}' (Parent ID: {dup['parent_id']})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Duplicate Count:** {dup['count']}")
                            st.write(f"**Child IDs:** {', '.join(map(str, dup['child_ids']))}")
                        
                        with col2:
                            if st.button(f"🔧 Jump to Editor", key=f"dup_{dup['parent_id']}"):
                                st.session_state['selected_parent_id'] = dup['parent_id']
                                st.switch_page("pages/1_Editor.py")
            else:
                st.info("No duplicate label conflicts found matching the search criteria")
        else:
            st.info("No duplicate label conflicts found")
            
    except Exception as e:
        st.error(f"Failed to load duplicate labels: {str(e)}")

# Orphan Nodes Validation
if check_orphans:
    st.header("👻 Orphan Nodes")
    
    try:
        orphans = get_json(f"/tree/conflicts/orphans?limit={page_size}&offset={offset}")
        
        if orphans:
            # Filter by search query if provided
            if search_query:
                filtered_orphans = []
                for orphan in orphans:
                    if (search_query.lower() in orphan.get('label', '').lower() or
                        search_query in str(orphan.get('id', '')) or
                        search_query in str(orphan.get('parent_id', ''))):
                        filtered_orphans.append(orphan)
                orphans = filtered_orphans
            
            if filtered_orphans:
                st.warning(f"Found {len(filtered_orphans)} orphan nodes")
                
                for orphan in filtered_orphans:
                    with st.expander(f"👻 Node {orphan['id']}: '{orphan['label']}' (Parent ID: {orphan['parent_id']})"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Node ID:** {orphan['id']}")
                            st.write(f"**Depth:** {orphan['depth']}")
                            st.write(f"**Invalid Parent ID:** {orphan['parent_id']}")
                        
                        with col2:
                            st.error("⚠️ This node references a non-existent parent")
                            if st.button(f"🔧 Jump to Node", key=f"orphan_{orphan['id']}"):
                                st.session_state['selected_node_id'] = orphan['id']
                                st.switch_page("pages/1_Editor.py")
            else:
                st.info("No orphan nodes found matching the search criteria")
        else:
            st.info("No orphan nodes found (database is healthy)")
            
    except Exception as e:
        st.error(f"Failed to load orphan nodes: {str(e)}")

# Depth Anomalies Validation
if check_depth:
    st.header("📏 Depth Anomalies")
    
    try:
        anomalies = get_json(f"/tree/conflicts/depth-anomalies?limit={page_size}&offset={offset}")
        
        if anomalies:
            # Filter by search query if provided
            if search_query:
                filtered_anomalies = []
                for anomaly in anomalies:
                    if (search_query.lower() in anomaly.get('label', '').lower() or
                        search_query in str(anomaly.get('id', '')) or
                        search_query in str(anomaly.get('parent_id', ''))):
                        filtered_anomalies.append(anomaly)
                anomalies = filtered_anomalies
            
            if filtered_anomalies:
                st.error(f"Found {len(filtered_anomalies)} depth anomalies")
                
                for anomaly in filtered_anomalies:
                    anomaly_type = anomaly['anomaly']
                    if anomaly_type == 'ROOT_DEPTH':
                        title = f"📏 Root Depth Error: Node {anomaly['id']}"
                        description = f"Root node has depth {anomaly['depth']} (should be 0)"
                    else:
                        title = f"📏 Parent-Child Depth Error: Node {anomaly['id']}"
                        description = f"Child depth {anomaly['depth']} doesn't match parent + 1"
                    
                    with st.expander(title):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Node ID:** {anomaly['id']}")
                            st.write(f"**Label:** {anomaly['label']}")
                            st.write(f"**Current Depth:** {anomaly['depth']}")
                            if anomaly['parent_id']:
                                st.write(f"**Parent ID:** {anomaly['parent_id']}")
                            st.write(f"**Anomaly Type:** {anomaly_type}")
                        
                        with col2:
                            st.error(description)
                            if anomaly['parent_id']:
                                if st.button(f"🔧 Jump to Parent", key=f"anomaly_parent_{anomaly['id']}"):
                                    st.session_state['selected_parent_id'] = anomaly['parent_id']
                                    st.switch_page("pages/1_Editor.py")
                            else:
                                if st.button(f"🔧 Jump to Node", key=f"anomaly_node_{anomaly['id']}"):
                                    st.session_state['selected_node_id'] = anomaly['id']
                                    st.switch_page("pages/1_Editor.py")
            else:
                st.info("No depth anomalies found matching the search criteria")
        else:
            st.success("✅ No depth anomalies found (tree structure is valid)")
            
    except Exception as e:
        st.error(f"Failed to load depth anomalies: {str(e)}")

# Pagination navigation
if check_duplicates or check_orphans or check_depth:
    st.divider()
    st.header("📄 Pagination")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⬅️ Previous Page", disabled=page_number == 0):
            st.session_state['page_number'] = page_number - 1
            st.rerun()
    
    with col2:
        st.write(f"**Page {page_number + 1}**")
    
    with col3:
        if st.button("➡️ Next Page"):
            st.session_state['page_number'] = page_number + 1
            st.rerun()
    
    with col4:
        if st.button("🔄 Reset to Page 0"):
            st.session_state['page_number'] = 0
            st.rerun()

# Legacy missing slots functionality (keeping for backward compatibility)
st.divider()
st.header("🔍 Missing Slots")

if st.button("Load Missing Slots"):
    try:
        missing_slots = get_json("/tree/missing-slots")
        if missing_slots:
            st.warning(f"Found {len(missing_slots)} parents with missing slots")
            
            for parent in missing_slots:
                with st.expander(f"Parent {parent['parent_id']}: '{parent['label']}'"):
                    st.write(f"**Missing Slots:** {parent['missing_slots']}")
                    if st.button(f"Jump to Editor", key=f"missing_{parent['parent_id']}"):
                        st.session_state['selected_parent_id'] = parent['parent_id']
                        st.switch_page("pages/1_Editor.py")
        else:
            st.success("✅ All parents have exactly 5 children")
            
    except Exception as e:
        st.error(f"Failed to load missing slots: {str(e)}")

if st.button("Find Next Incomplete"):
    try:
        next_incomplete = get_json("/tree/next-incomplete-parent")
        st.success(f"Next incomplete parent: {next_incomplete['parent_id']}")
        
        if st.button("Jump to Next Incomplete"):
            st.session_state['selected_parent_id'] = next_incomplete['parent_id']
            st.switch_page("pages/1_Editor.py")
            
    except Exception as e:
        st.error(f"Failed to find next incomplete parent: {str(e)}")
