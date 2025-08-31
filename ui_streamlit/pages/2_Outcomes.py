import streamlit as st
import requests
from ui_streamlit.api_client import get_json, put_json

st.set_page_config(
    page_title="Outcomes - Lorien",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Outcomes Management")
st.caption("Edit triage outcomes and actions for leaf nodes")

# Navigation
col1, col2 = st.columns(2)
with col1:
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("Home.py")
with col2:
    if st.button("✏️ Editor", use_container_width=True):
        st.switch_page("pages/1_Editor.py")

# Search and filter
st.header("🔍 Search Outcomes")
col1, col2 = st.columns(2)

with col1:
    search_query = st.text_input("Search by triage text or actions", placeholder="e.g., chest pain, urgent care")

with col2:
    vm_filter = st.text_input("Vital Measurement filter", placeholder="e.g., Chest Pain Assessment")

# Copy From last VM functionality
def _copy_from_last_vm(vm_label: str):
    """Copy triage and actions from the last Vital Measurement"""
    try:
        # Search for outcomes with the specified VM
        search_params = {"leaf_only": "true"}
        if vm_label:
            search_params["query"] = vm_label
        
        results = get_json("/triage/search", params=search_params)
        
        if results and len(results) > 0:
            # Filter by vital measurement if specified
            vm_results = []
            for result in results:
                if vm_label.lower() in result.get('vital_measurement', '').lower():
                    vm_results.append(result)
            
            if vm_results:
                # Sort by updated_at to get the latest
                vm_results.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
                latest = vm_results[0]
                
                # Populate session state with the latest outcome
                st.session_state["triage_text"] = latest.get('triage', '')
                st.session_state["actions_text"] = latest.get('actions', '')
                
                st.success(f"✅ Copied from latest {vm_label} outcome")
                return True
            else:
                st.warning(f"⚠️ No outcomes found for Vital Measurement: {vm_label}")
                return False
        else:
            st.warning("⚠️ No outcomes found")
            return False
            
    except Exception as e:
        st.error(f"Error copying from last VM: {str(e)[:100]}...")
        return False

# Copy From last VM button
if st.button("📋 Copy From last VM", use_container_width=True):
    if vm_filter:
        _copy_from_last_vm(vm_filter)
    else:
        st.warning("Please enter a Vital Measurement filter first")

# Search outcomes
try:
    if search_query or vm_filter:
        search_params = {"leaf_only": "true"}
        if search_query:
            search_params["query"] = search_query
        
        results = get_json("/triage/search", params=search_params)
        
        if not results:
            st.info("📋 No outcomes found matching your search criteria")
            st.markdown("""
            **To get started with outcomes:**
            1. **Import Data**: Use Workspace to import Excel workbooks with triage data
            2. **Create Trees**: Use Editor to build decision trees with leaf nodes
            3. **Add Outcomes**: Edit leaf nodes to include triage and actions
            4. **Search & Filter**: Use the search tools above to find specific outcomes
            """)
            st.stop()
        
        st.success(f"Found {len(results)} outcomes")
        
        # Display results
        for outcome in results:
            with st.expander(f"Node {outcome.get('node_id', 'Unknown')}: {outcome.get('vital_measurement', 'No VM')}"):
                st.write(f"**Triage:** {outcome.get('triage', 'No triage data')}")
                st.write(f"**Actions:** {outcome.get('actions', 'No actions data')}")
                st.write(f"**Updated:** {outcome.get('updated_at', 'Unknown')}")
                
                # Edit button
                if st.button(f"✏️ Edit Node {outcome.get('node_id', 'Unknown')}", key=f"edit_{outcome.get('node_id', 'Unknown')}"):
                    st.session_state["editing_node_id"] = outcome.get('node_id')
                    st.session_state["triage_text"] = outcome.get('triage', '')
                    st.session_state["actions_text"] = outcome.get('actions', '')
                    st.rerun()
    
    else:
        st.info("🔍 Use the search fields above to find outcomes")
        
except Exception as e:
    st.error(f"Error searching outcomes: {str(e)[:100]}...")
    st.info("Please check your API connection in Settings")

# Edit outcomes
st.header("✏️ Edit Outcomes")

# Initialize session state for editing
if "editing_node_id" not in st.session_state:
    st.session_state["editing_node_id"] = None
if "triage_text" not in st.session_state:
    st.session_state["triage_text"] = ""
if "actions_text" not in st.session_state:
    st.session_state["actions_text"] = ""

if st.session_state["editing_node_id"]:
    node_id = st.session_state["editing_node_id"]
    st.subheader(f"Editing Node {node_id}")
    
    # Triage text area
    triage_text = st.text_area(
        "Diagnostic Triage",
        value=st.session_state["triage_text"],
        height=150,
        placeholder="Enter diagnostic triage information...",
        help="Describe the diagnostic assessment and triage decision"
    )
    
    # Actions text area
    actions_text = st.text_area(
        "Recommended Actions",
        value=st.session_state["actions_text"],
        height=150,
        placeholder="Enter recommended actions...",
        help="List specific actions, referrals, or next steps"
    )
    
    # Save and cancel buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("💾 Save Changes", type="primary"):
            if triage_text.strip() or actions_text.strip():
                try:
                    # Update the outcome
                    result = put_json(f"/triage/{node_id}", {
                        "triage": triage_text.strip(),
                        "actions": actions_text.strip()
                    })
                    
                    st.success(f"✅ Outcome for node {node_id} updated successfully")
                    
                    # Clear editing state
                    del st.session_state["editing_node_id"]
                    del st.session_state["triage_text"]
                    del st.session_state["actions_text"]
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error saving outcome: {str(e)[:100]}...")
            else:
                st.warning("Please enter triage or actions text")
    
    with col2:
        if st.button("❌ Cancel"):
            # Clear editing state
            del st.session_state["editing_node_id"]
            del st.session_state["triage_text"]
            del st.session_state["actions_text"]
            st.rerun()

else:
    st.info("📝 Select an outcome above to edit, or use 'Copy From last VM' to populate fields")

# Help section
st.header("❓ Outcomes Help")
st.markdown("""
**Outcomes Management:**
- 📋 **Triage**: Diagnostic assessment and decision-making
- **Actions**: Specific recommendations and next steps
- **Leaf Nodes**: Only leaf nodes (no children) can have outcomes
- **Copy From VM**: Reuse successful outcomes from previous cases

**Best Practices:**
1. **Be Specific**: Include clear diagnostic criteria
2. **Actionable**: Provide concrete next steps
3. **Consistent**: Use standardized terminology
4. **Review**: Regularly update based on outcomes

**Workflow:**
1. **Search** for existing outcomes
2. **Copy** from similar cases if available
3. **Edit** triage and actions as needed
4. **Save** changes to update the node
5. **Review** outcomes for quality and consistency
""")
