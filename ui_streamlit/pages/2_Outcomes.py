import streamlit as st
from ui_streamlit.api_client import get_json, put_json

st.set_page_config(page_title="Outcomes", layout="wide")

st.title("Outcomes & Triage")

# Search and Filter
st.header("Search & Filter")
search_query = st.text_input("Search in triage/actions")
leaf_only = st.checkbox("Leaf nodes only", value=True)

if st.button("Search"):
    try:
        params = {"leaf_only": leaf_only}
        if search_query:
            params["query"] = search_query
            
        results = get_json("/triage/search", params=params)
        st.session_state['triage_results'] = results["results"]
        st.success(f"Found {results['total_count']} results")
    except Exception as e:
        st.error(f"Search failed: {str(e)}")

# Triage Grid
if 'triage_results' in st.session_state and st.session_state['triage_results']:
    st.header("Triage Results")
    
    # Multi-select for comparison
    selected_indices = st.multiselect(
        "Select rows for comparison",
        range(len(st.session_state['triage_results'])),
        format_func=lambda x: f"Node {st.session_state['triage_results'][x]['node_id']}"
    )
    
    # Show selected rows for comparison
    if selected_indices:
        st.subheader("Selected for Comparison (Read-only)")
        for idx in selected_indices:
            result = st.session_state['triage_results'][idx]
            with st.expander(f"Node {result['node_id']}: {result.get('path', 'N/A')}"):
                st.write(f"**Diagnostic Triage:** {result.get('diagnostic_triage', 'N/A')}")
                st.write(f"**Actions:** {result.get('actions', 'N/A')}")
                st.write(f"**Updated:** {result.get('updated_at', 'N/A')}")
    
    # Main grid with inline editing
    for i, result in enumerate(st.session_state['triage_results']):
        with st.expander(f"Node {result['node_id']}: {result.get('path', 'N/A')}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Current Values:**")
                st.write(f"Diagnostic Triage: {result.get('diagnostic_triage', 'N/A')}")
                st.write(f"Actions: {result.get('actions', 'N/A')}")
            
            with col2:
                st.write("**Edit (Leaf nodes only):**")
                if result.get('is_leaf', False):
                    new_triage = st.text_area("Diagnostic Triage", value=result.get('diagnostic_triage', ''), key=f"triage_{i}")
                    new_actions = st.text_area("Actions", value=result.get('actions', ''), key=f"actions_{i}")
                    
                    if st.button("Save Changes", key=f"save_{i}"):
                        try:
                            update_result = put_json(f"/triage/{result['node_id']}", {
                                "diagnostic_triage": new_triage,
                                "actions": new_actions
                            })
                            st.success("Triage updated successfully!")
                            # Refresh the data
                            st.rerun()
                        except Exception as e:
                            st.error(f"Update failed: {str(e)}")
                else:
                    st.warning("⚠️ Non-leaf nodes cannot be edited")
                    st.info("Only leaf nodes support triage editing")

# Show message if no results
elif 'triage_results' in st.session_state and not st.session_state['triage_results']:
    st.info("No triage results found. Try adjusting your search criteria.")

# Initial state
else:
    st.info("Click 'Search' to find triage records.")
