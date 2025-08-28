from __future__ import annotations
import streamlit as st
from ui_streamlit.components import top_health_banner, error_message
from ui_streamlit.api_client import get_next_incomplete_parent, get_children, upsert_children

st.set_page_config(page_title="Editor", layout="wide")
st.title("Editor — Parent (5 child slots)")

top_health_banner()

st.markdown("Use **Skip to next incomplete parent** to focus curation.")

# Parent ID input
parent_id = st.text_input("Parent ID", value="1", key="editor_parent_id")

col1, col2 = st.columns([1,1])
if col1.button("Skip to next incomplete parent", type="primary"):
    try:
        data = get_next_incomplete_parent()
        if not data:
            st.success("No incomplete parents found.")
        else:
            pid = data.get("parent_id")
            st.session_state["last_incomplete_parent"] = pid
            st.session_state["editor_parent_id"] = str(pid)
            st.success(f"Next incomplete parent: {pid}")
            st.page_link("pages/2_Parent_Detail.py", label="Open Parent Detail", icon="➡️")
    except Exception as e:
        error_message(e)

if col2.button("Load Children"):
    try:
        data = get_children(int(parent_id))
        st.session_state["children"] = data
        st.success(f"Loaded {len(data)} children for parent {parent_id}")
    except Exception as e:
        error_message(e)

# Initialize children data
if "children" not in st.session_state:
    st.session_state["children"] = []

# Display and edit children
st.subheader("Child Slots (1-5)")
edited_children = []

for slot in range(1, 6):
    # Find existing child for this slot
    existing_child = next((c for c in st.session_state["children"] if c.get("slot") == slot), None)
    current_label = existing_child.get("label", "") if existing_child else ""
    
    # Create input for this slot
    new_label = st.text_input(
        f"Slot {slot}", 
        value=current_label, 
        key=f"slot_{slot}",
        placeholder=f"Enter label for slot {slot}"
    )
    
    edited_children.append({
        "slot": slot,
        "label": new_label
    })

# Save button with validation
if st.button("Save (atomic upsert)", type="primary"):
    try:
        # Guard: validate exactly 5 slots without duplicates
        slots = [c["slot"] for c in edited_children]
        if len(slots) != 5:
            st.error("Must have exactly 5 slots")
        elif len(set(slots)) != 5:
            st.error("Duplicate slots detected")
        elif not all(1 <= slot <= 5 for slot in slots):
            st.error("Slots must be 1-5")
        else:
            # Prepare payload
            payload = {"children": edited_children}
            
            # Perform atomic upsert
            result = upsert_children(int(parent_id), edited_children)
            
            # Update session state
            st.session_state["children"] = edited_children
            
            st.success("Saved successfully!")
            st.json(result)
            
    except Exception as e:
        error_message(e)

st.info("Tip: Use the Settings page to configure API base URL if needed.")
