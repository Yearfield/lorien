import streamlit as st
from ui_streamlit.api_client import get_json

st.set_page_config(page_title="Conflicts", layout="wide")

st.title("Conflicts & Integrity")

# Missing Slots Section
st.header("Missing Slots")
if st.button("Load Missing Slots"):
    try:
        missing_data = get_json("/tree/missing-slots")
        if missing_data["parents_with_missing_slots"]:
            st.subheader(f"Found {missing_data['total_count']} parents with missing slots")
            
            for parent in missing_data["parents_with_missing_slots"]:
                with st.expander(f"Parent {parent['parent_id']}: {parent['label']}"):
                    st.write(f"Missing slots: {parent['missing_slots']}")
                    if st.button(f"Jump to Parent {parent['parent_id']}", key=f"jump_{parent['parent_id']}"):
                        st.session_state['selected_parent_id'] = parent['parent_id']
                        st.success(f"Selected Parent {parent['parent_id']} - use Parent Detail page to view")
        else:
            st.success("No missing slots found!")
    except Exception as e:
        st.error(f"Failed to load missing slots: {str(e)}")

# Next Incomplete Parent Section
st.header("Next Incomplete Parent")
if st.button("Find Next Incomplete"):
    try:
        next_incomplete = get_json("/tree/next-incomplete-parent")
        if next_incomplete:
            st.success(f"Next incomplete parent: {next_incomplete['parent_id']}")
            st.write(f"Missing slots: {next_incomplete['missing_slots']}")
            
            if st.button("Jump to Parent Detail"):
                st.session_state['selected_parent_id'] = next_incomplete['parent_id']
                st.success(f"Selected Parent {next_incomplete['parent_id']} - use Parent Detail page to view")
        else:
            st.info("No incomplete parents found")
    except Exception as e:
        st.error(f"Failed to find next incomplete parent: {str(e)}")

# Search and Filters
st.header("Search & Filters")
search_query = st.text_input("Search by parent label or ID")
if search_query:
    try:
        # This would need a search endpoint - for now, show current selection
        if 'selected_parent_id' in st.session_state:
            st.info(f"Currently selected: Parent {st.session_state['selected_parent_id']}")
    except Exception as e:
        st.error(f"Search failed: {str(e)}")

# Show current selection
if 'selected_parent_id' in st.session_state:
    st.header("Current Selection")
    st.info(f"Selected Parent ID: {st.session_state['selected_parent_id']}")
    st.write("Use the Parent Detail page to view and edit this parent's children.")
