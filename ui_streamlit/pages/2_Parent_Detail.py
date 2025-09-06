from __future__ import annotations
import streamlit as st
import requests
import json
from ui_streamlit.components import top_health_banner, error_message
from ui_streamlit.api_client import get_children, upsert_children, get_next_incomplete_parent, get_json, put_json
from ui_streamlit.settings import get_api_base_url

st.set_page_config(
    page_title="Parent Detail - Lorien",
    page_icon="✏️",
    layout="wide"
)

st.title("✏️ Parent Detail Editor")
st.caption("Edit parent node and manage child slots")

# Navigation
col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")
with col2:
    if st.button("📝 Editor", use_container_width=True):
        st.switch_page("pages/1_Editor.py")

# Parent ID input
parent_id = st.text_input(
    "Parent ID",
    value=st.session_state.get("detail_parent_id", "1"),
    help="Enter the parent node ID to edit"
)

if parent_id:
    st.session_state["detail_parent_id"] = parent_id
    
    # Skip to next incomplete functionality
    if st.button("⏭️ Jump to Next Incomplete", use_container_width=True):
        try:
            next_incomplete = get_json("/tree/next-incomplete-parent")
            if next_incomplete and "id" in next_incomplete:
                new_parent_id = str(next_incomplete["id"])
                st.session_state["detail_parent_id"] = new_parent_id
                
                # Refresh the parents list
                try:
                    children = get_json(f"/tree/{new_parent_id}/children")
                    st.session_state["parents_list"] = children
                except:
                    pass
                
                st.info(f"Jumped to next incomplete parent: {new_parent_id}")
                
                # Add focus anchor for auto-scrolling
                st.markdown(f"<a id='focus-{new_parent_id}'></a>", unsafe_allow_html=True)
                
                # Trigger page refresh to show new parent
                st.rerun()
            else:
                st.success("✅ All parents are complete!")
        except Exception as e:
            st.error(f"Error finding next incomplete parent: {str(e)[:100]}...")
    
    # Get parent details
    try:
        parent_data = get_json(f"/tree/{parent_id}")
        children = get_json(f"/tree/{parent_id}/children")
        
        # Store in session state for Editor page
        st.session_state["parents_list"] = children
        
        st.header(f"Parent {parent_id}: {parent_data.get('label', 'No label')}")
        st.write(f"**Depth:** {parent_data.get('depth', 'Unknown')}")
        st.write(f"**Type:** {parent_data.get('type', 'Unknown')}")
        
        # Children management
        st.subheader("👶 Children")

        # Bulk edit mode toggle
        bulk_edit = st.checkbox("Enable Bulk Edit Mode", value=False)

        if bulk_edit:
            # Bulk edit mode - edit all 5 slots at once
            st.info("⚡ Bulk Edit Mode: Edit all 5 child slots and save at once")

            # Initialize 5 slots
            slot_labels = ["", "", "", "", ""]

            # Populate existing children
            for child in children:
                slot_idx = child.get('slot', 0) - 1  # Convert 1-based to 0-based
                if 0 <= slot_idx < 5:
                    slot_labels[slot_idx] = child.get('label', '')

            # Input fields for all 5 slots
            st.write("**Edit all 5 child slots:**")
            new_slot_labels = []
            for i in range(5):
                label = st.text_input(
                    f"Slot {i+1}",
                    value=slot_labels[i],
                    key=f"bulk_slot_{i}"
                )
                new_slot_labels.append(label)

            # Save bulk changes
            if st.button("💾 Save All Changes", type="primary", use_container_width=True):
                try:
                    # Prepare children data for bulk update
                    children_data = []
                    for i in range(5):
                        if new_slot_labels[i].strip():
                            children_data.append({
                                "slot": i + 1,
                                "label": new_slot_labels[i].strip()
                            })

                    if children_data:
                        result = put_json(f"/tree/{parent_id}/children", {
                            "children": children_data
                        })
                        st.success("✅ All child slots updated successfully!")
                        st.rerun()
                    else:
                        st.warning("Please fill at least one child slot")
                except Exception as e:
                    st.error(f"Error updating children: {str(e)[:100]}...")

        else:
            # Individual edit mode
            if children:
                for i, child in enumerate(children):
                    with st.expander(f"Slot {child.get('slot', i+1)}: {child.get('label', 'No label')}"):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            new_label = st.text_input(
                                f"Label for Slot {child.get('slot', i+1)}",
                                value=child.get('label', ''),
                                key=f"label_{child['id']}"
                            )
                        with col2:
                            if st.button("💾 Save", key=f"save_{child['id']}"):
                                try:
                                    updated = put_json(f"/tree/{child['id']}", {"label": new_label})
                                    st.success(f"Updated child {child['id']}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating child: {str(e)[:100]}...")
            else:
                st.info("No children found for this parent")
            
        # Add new child
        st.subheader("➕ Add New Child")
        new_child_label = st.text_input("New child label")
        if st.button("Add Child"):
            if new_child_label:
                try:
                    # Find next available slot
                    used_slots = {child.get('slot', 0) for child in children}
                    next_slot = 1
                    while next_slot in used_slots:
                        next_slot += 1
                    
                    if next_slot <= 5:  # Enforce 5-child limit
                        new_child = put_json(f"/tree/{parent_id}/children", {
                            "label": new_child_label,
                            "slot": next_slot
                        })
                        st.success(f"Added child in slot {next_slot}")
                        st.rerun()
                    else:
                        st.error("Parent already has 5 children")
                except Exception as e:
                    st.error(f"Error adding child: {str(e)[:100]}...")
            else:
                st.warning("Please enter a label for the new child")
                
    except Exception as e:
        st.error(f"Error loading parent {parent_id}: {str(e)[:100]}...")
        st.info("Please check the parent ID and try again")
