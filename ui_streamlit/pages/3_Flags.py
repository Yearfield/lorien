from __future__ import annotations
import streamlit as st
from ui_streamlit.components import top_health_banner, error_message
from ui_streamlit.api_client import flags_search, flags_assign

st.set_page_config(page_title="Flags", layout="wide")
st.title("Flags")
top_health_banner()

st.markdown("Search and assign red flags to nodes (node-by-node for beta)")

# Node selection
node_id = st.number_input("Node ID", min_value=1, step=1, value=1)

# Cascade toggle
cascade = st.checkbox("Assign to branch (parent + descendants)", value=False, help="When enabled, applies the flag to the selected node and all its descendants")

# Flag search
q = st.text_input("Search flags", placeholder="Enter flag name to search...")
if q:
    try:
        results = flags_search(q)
        if results:
            st.success(f"Found {len(results)} flag(s)")
            
            for item in results:
                with st.container():
                    st.markdown(f"**{item.get('name')}**")
                    if item.get('description'):
                        st.caption(item.get('description'))
                    if item.get('severity'):
                        st.caption(f"Severity: {item.get('severity')}")
                    
                    # Assignment form
                    with st.form(key=f"assign_{item['id']}"):
                        assigned_node = st.number_input(
                            "Assign to Node ID", 
                            min_value=1, 
                            value=node_id,
                            key=f"node_{item['id']}"
                        )
                        user = st.text_input("User (optional)", key=f"user_{item['id']}")
                        submitted = st.form_submit_button("Assign to node")
                        
                        if submitted:
                            try:
                                # Update the API client call to include cascade and user parameters
                                result = flags_assign(assigned_node, item.get("name", ""), user if user.strip() else None, cascade)
                                st.success(f"Assigned '{item.get('name')}' to node {assigned_node}" + (" and descendants" if cascade else ""))
                                st.json(result)
                            except Exception as e:
                                error_message(e)
        else:
            st.info("No flags found matching your search.")
    except Exception as e:
        error_message(e)
else:
    st.info("Enter a search term to find flags.")
