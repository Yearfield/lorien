from __future__ import annotations
import streamlit as st
from ui_streamlit.api_client import get_json

st.set_page_config(
    page_title="Editor - Lorien",
    page_icon="✏️",
    layout="wide"
)

st.title("✏️ Tree Editor")
st.caption("Manage decision tree structure and parent-child relationships")

# Navigation
if st.button("🏠 Home", use_container_width=True):
    st.switch_page("Home.py")

# Initialize parents list in session state
if "parents_list" not in st.session_state:
    st.session_state["parents_list"] = []

# Refresh button
if st.button("🔄 Refresh", use_container_width=True):
    try:
        missing_slots = get_json("/tree/missing-slots")
        st.session_state["parents_list"] = missing_slots
        st.success(f"Refreshed: Found {len(missing_slots)} parents with missing slots")
    except Exception as e:
        st.error(f"Error refreshing: {str(e)[:100]}...")

# Display parents with missing slots
st.header("📋 Parents with Missing Slots")

if st.session_state["parents_list"]:
    for parent in st.session_state["parents_list"]:
        parent_id = parent.get("id")
        missing_slots = parent.get("missing_slots", [])
        
        # Create focus anchor for each parent
        st.markdown(f"<div id='focus-{parent_id}'></div>", unsafe_allow_html=True)
        
        with st.expander(f"Parent {parent_id}: {parent.get('label', 'No label')} - Missing: {missing_slots}"):
            st.write(f"**Depth:** {parent.get('depth', 'Unknown')}")
            st.write(f"**Missing slots:** {missing_slots}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✏️ Edit Parent {parent_id}", key=f"edit_{parent_id}"):
                    st.session_state["detail_parent_id"] = str(parent_id)
                    st.switch_page("pages/2_Parent_Detail.py")
            with col2:
                if st.button(f"📊 View Details", key=f"view_{parent_id}"):
                    st.session_state["detail_parent_id"] = str(parent_id)
                    st.switch_page("pages/2_Parent_Detail.py")
else:
    st.info("No parents with missing slots found. All trees are complete!")

# Quick actions
st.header("⚡ Quick Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("⏭️ Find Next Incomplete", use_container_width=True):
        try:
            next_incomplete = get_json("/tree/next-incomplete-parent")
            if next_incomplete and "id" in next_incomplete:
                parent_id = str(next_incomplete["id"])
                st.session_state["detail_parent_id"] = parent_id
                st.info(f"Found next incomplete parent: {parent_id}")
                st.switch_page("pages/2_Parent_Detail.py")
            else:
                st.success("✅ All parents are complete!")
        except Exception as e:
            st.error(f"Error finding next incomplete: {str(e)[:100]}...")

with col2:
    if st.button("🏗️ Create New Vital Measurement", use_container_width=True):
        st.info("Navigate to Workspace to create new Vital Measurements")

# Create new Vital Measurement form
st.header("🏗️ Create New Vital Measurement")
with st.expander("New Vital Measurement Form"):
    new_vm_label = st.text_input("Vital Measurement Label", placeholder="e.g., Chest Pain Assessment")
    children_labels = []
    
    st.write("**Child Labels (optional):**")
    for i in range(5):
        child_label = st.text_input(f"Child {i+1}", key=f"child_{i}")
        if child_label:
            children_labels.append(child_label)
    
    if st.button("Create Vital Measurement"):
        if new_vm_label:
            try:
                # Create root with children
                payload = {"label": new_vm_label}
                if children_labels:
                    payload["children"] = children_labels
                
                result = get_json("/tree/roots", method="POST", data=payload)
                st.success(f"Created Vital Measurement: {result.get('root_id', 'Unknown')}")
                st.info("Navigate to Parent Detail to edit the new tree")
            except Exception as e:
                st.error(f"Error creating Vital Measurement: {str(e)[:100]}...")
        else:
            st.warning("Please enter a Vital Measurement label")

# Summary
st.header("📊 Summary")
st.markdown("""
**Editor Workflow:**
1. **Review** parents with missing slots above
2. **Click Edit** to manage specific parent's children
3. **Use Quick Actions** to jump to next incomplete parent
4. **Create new** Vital Measurements as needed
5. **Ensure** each parent has exactly 5 children
""")
