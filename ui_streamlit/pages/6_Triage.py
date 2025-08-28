from __future__ import annotations
import streamlit as st
from ui_streamlit.components import top_health_banner, error_message
from ui_streamlit.api_client import get_triage, put_triage, get_children

st.set_page_config(page_title="Triage", layout="wide")
st.title("Triage Management")
top_health_banner()

st.markdown("Edit triage information for leaf nodes only.")

# Node selection
node_id = st.number_input("Node ID", min_value=1, step=1, value=1)

# Check if node is a leaf
if st.button("Check Node Type"):
    try:
        children = get_children(node_id)
        if not children:
            st.warning("Node has no children - may be a leaf")
        else:
            st.info(f"Node has {len(children)} children - not a leaf")
            st.write("Children:", [f"Slot {c.get('slot')}: {c.get('label')}" for c in children])
    except Exception as e:
        error_message(e)

# Load triage data
if st.button("Load Triage"):
    try:
        triage_data = get_triage(node_id)
        st.session_state["triage"] = triage_data
        st.success("Triage data loaded")
    except Exception as e:
        if "404" in str(e):
            st.info("No triage data found for this node")
        else:
            error_message(e)

# Display and edit triage
if "triage" in st.session_state:
    triage = st.session_state["triage"]
    
    st.subheader("Current Triage Data")
    st.json(triage)
    
    # Edit form
    st.subheader("Edit Triage")
    with st.form("edit_triage"):
        diagnostic_triage = st.text_area(
            "Diagnostic Triage",
            value=triage.get("diagnostic_triage", ""),
            placeholder="Enter diagnostic triage information..."
        )
        
        actions = st.text_area(
            "Actions",
            value=triage.get("actions", ""),
            placeholder="Enter actions to take..."
        )
        
        submitted = st.form_submit_button("Update Triage")
        
        if submitted:
            try:
                # Validate that at least one field is provided
                if not diagnostic_triage.strip() and not actions.strip():
                    st.error("At least one field (diagnostic_triage or actions) must be provided")
                else:
                    # Prepare update payload
                    update_data = {}
                    if diagnostic_triage.strip():
                        update_data["diagnostic_triage"] = diagnostic_triage.strip()
                    if actions.strip():
                        update_data["actions"] = actions.strip()
                    
                    # Update triage
                    result = put_triage(node_id, update_data)
                    st.success("Triage updated successfully!")
                    st.json(result)
                    
                    # Refresh triage data
                    st.session_state["triage"] = get_triage(node_id)
                    
            except Exception as e:
                error_message(e)
else:
    st.info("Load triage data to edit.")

# Leaf-only enforcement info
st.info("""
**Leaf-Only Policy:**
- Triage editing is only available for leaf nodes (nodes with no children)
- This ensures triage information is only applied to terminal decision points
- Use the "Check Node Type" button to verify if a node is a leaf
""")
