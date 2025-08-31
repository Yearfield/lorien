import streamlit as st
from ui_streamlit.api_client import get_json

st.set_page_config(
    page_title="Conflicts - Lorien",
    page_icon="⚠️",
    layout="wide"
)

st.title("⚠️ Conflicts & Data Integrity")
st.caption("Identify and resolve data conflicts in your decision trees")

# Navigation
if st.button("🏠 Home", use_container_width=True):
    st.switch_page("Home.py")

# Missing Slots
st.header("🔍 Missing Slots")
try:
    missing_slots = get_json("/tree/missing-slots")
    if missing_slots:
        st.warning(f"Found {len(missing_slots)} parents with missing child slots")
        
        # Filters
        st.subheader("🔍 Filters")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            depth_filter = st.selectbox("Depth", ["Any"] + list(range(1, 6)), key="depth_filter")
        with col2:
            label_filter = st.text_input("Label contains", key="label_filter")
        with col3:
            parent_id_filter = st.text_input("Parent ID", key="parent_id_filter")
        
        # Apply filters
        filtered_slots = missing_slots
        if depth_filter != "Any":
            filtered_slots = [p for p in filtered_slots if p.get("depth") == depth_filter]
        if label_filter:
            filtered_slots = [p for p in filtered_slots if label_filter.lower() in p.get("label", "").lower()]
        if parent_id_filter:
            filtered_slots = [p for p in filtered_slots if str(p.get("parent_id")) == parent_id_filter]
        
        st.info(f"Showing {len(filtered_slots)} of {len(missing_slots)} results")
        
        # Bulk operations
        if filtered_slots:
            if st.button("🚀 Open All in Editor", use_container_width=True):
                st.info(f"Opening {min(len(filtered_slots), 50)} parents in Editor (capped to avoid UI lock)")
                # In a real implementation, this would navigate to editor with the filtered list
                st.success("✅ Ready to edit filtered parents")
        
        # Display filtered results
        for parent in filtered_slots:
            with st.expander(f"Parent {parent['id']}: {parent.get('label', 'No label')}"):
                st.write(f"**Depth:** {parent.get('depth', 'Unknown')}")
                st.write(f"**Missing slots:** {parent.get('missing_slots', [])}")
                if st.button(f"Jump to Editor", key=f"edit_{parent['id']}"):
                    st.switch_page("pages/1_Editor.py")
    else:
        st.success("✅ All parents have complete child slots")
except Exception as e:
    st.warning(f"⚠️ Could not fetch missing slots: {str(e)[:100]}...")

# Duplicate Labels
st.header("🔄 Duplicate Labels")
try:
    duplicate_labels = get_json("/tree/conflicts/duplicate-labels")
    if duplicate_labels:
        st.warning(f"Found {len(duplicate_labels)} duplicate label conflicts")
        for conflict in duplicate_labels:
            with st.expander(f"Conflict: {conflict.get('label', 'No label')}"):
                st.write(f"**Parent ID:** {conflict.get('parent_id', 'Unknown')}")
                st.write(f"**Slot:** {conflict.get('slot', 'Unknown')}")
                st.write(f"**Node ID:** {conflict.get('node_id', 'Unknown')}")
    else:
        st.success("✅ No duplicate label conflicts found")
except Exception as e:
    st.warning(f"⚠️ Could not fetch duplicate labels: {str(e)[:100]}...")

# Orphans
st.header("👶 Orphaned Nodes")
try:
    orphans = get_json("/tree/conflicts/orphans")
    if orphans:
        st.warning(f"Found {len(orphans)} orphaned nodes")
        for orphan in orphans:
            with st.expander(f"Orphan: {orphan.get('label', 'No label')}"):
                st.write(f"**Node ID:** {orphan.get('id', 'Unknown')}")
                st.write(f"**Depth:** {orphan.get('depth', 'Unknown')}")
    else:
        st.success("✅ No orphaned nodes found")
except Exception as e:
    st.warning(f"⚠️ Could not fetch orphans: {str(e)[:100]}...")

# Depth Anomalies
st.header("📏 Depth Anomalies")
try:
    depth_anomalies = get_json("/tree/conflicts/depth-anomalies")
    if depth_anomalies:
        st.warning(f"Found {len(depth_anomalies)} depth anomalies")
        for anomaly in depth_anomalies:
            with st.expander(f"Anomaly: {anomaly.get('label', 'No label')}"):
                st.write(f"**Node ID:** {anomaly.get('id', 'Unknown')}")
                st.write(f"**Expected Depth:** {anomaly.get('expected_depth', 'Unknown')}")
                st.write(f"**Actual Depth:** {anomaly.get('actual_depth', 'Unknown')}")
    else:
        st.success("✅ No depth anomalies found")
except Exception as e:
    st.warning(f"⚠️ Could not fetch depth anomalies: {str(e)[:100]}...")

# Next Incomplete Parent
st.header("⏭️ Next Incomplete Parent")
try:
    next_incomplete = get_json("/tree/next-incomplete-parent")
    if next_incomplete:
        st.info(f"Next incomplete parent: {next_incomplete.get('id', 'Unknown')}")
        st.write(f"**Label:** {next_incomplete.get('label', 'No label')}")
        st.write(f"**Missing slots:** {next_incomplete.get('missing_slots', [])}")
        if st.button("Jump to Next Incomplete", use_container_width=True):
            st.switch_page("pages/2_Parent_Detail.py")
    else:
        st.success("✅ All parents are complete")
except Exception as e:
    st.warning(f"⚠️ Could not fetch next incomplete parent: {str(e)[:100]}...")

# Summary
st.header("📊 Summary")
st.markdown("""
**Conflict Resolution Workflow:**
1. **Review** conflicts above
2. **Jump to Editor** for specific parents
3. **Fix missing slots** by adding children
4. **Resolve duplicates** by renaming or removing
5. **Clean up orphans** by reassigning or deleting
6. **Verify depth** consistency across the tree
""")
