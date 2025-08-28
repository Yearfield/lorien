import streamlit as st
import requests
from ui_streamlit.api_client import get_json, put_json

st.set_page_config(page_title="Outcomes", page_icon="📋")

st.title("📋 Outcomes & Triage")

# LLM Status Check
llm_enabled = False
try:
    llm_health = get_json("/llm/health")
    llm_enabled = llm_health.get("status") == "ok"
except:
    llm_enabled = False

if llm_enabled:
    st.success("🤖 LLM Integration: Enabled")
else:
    st.warning("🤖 LLM Integration: Disabled (503 Service Unavailable)")

# Search and Filter
st.header("🔍 Search & Filter")
col1, col2 = st.columns(2)

with col1:
    leaf_only = st.checkbox("Leaf nodes only", value=True, help="Only show nodes that can have triage data")
    
with col2:
    search_query = st.text_input("Search in triage/actions", placeholder="e.g., pain, fever, emergency")

# Load triage data
if st.button("🔍 Search Triage Records"):
    try:
        params = {"leaf_only": leaf_only}
        if search_query:
            params["query"] = search_query
            
        results = get_json("/triage/search", params=params)
        
        if results and results.get("results"):
            st.success(f"Found {len(results['results'])} records")
            
            # Multi-select for comparison
            st.subheader("📊 Multi-Select for Comparison")
            all_records = results["results"]
            selected_indices = st.multiselect(
                "Select records to compare:",
                options=range(len(all_records)),
                format_func=lambda i: f"{all_records[i]['path']} (ID: {all_records[i]['node_id']})"
            )
            
            if selected_indices:
                st.subheader("📋 Selected Records")
                for idx in selected_indices:
                    record = all_records[idx]
                    with st.expander(f"📋 {record['path']} (ID: {record['node_id']})"):
                        st.write(f"**Depth:** {record['depth']}")
                        st.write(f"**Is Leaf:** {'✅ Yes' if record['is_leaf'] else '❌ No'}")
                        st.write(f"**Diagnostic Triage:** {record['diagnostic_triage'] or 'Not set'}")
                        st.write(f"**Actions:** {record['actions'] or 'Not set'}")
                        st.write(f"**Updated:** {record['updated_at'] or 'Never'}")
            
            # Main grid view
            st.subheader("📋 All Triage Records")
            for record in results["results"]:
                with st.expander(f"📋 {record['path']} (ID: {record['node_id']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Depth:** {record['depth']}")
                        st.write(f"**Is Leaf:** {'✅ Yes' if record['is_leaf'] else '❌ No'}")
                        st.write(f"**Updated:** {record['updated_at'] or 'Never'}")
                    
                    with col2:
                        if record['is_leaf']:
                            # LLM Fill button (only for leaves)
                            if llm_enabled:
                                if st.button(f"🤖 Fill with LLM", key=f"llm_{record['node_id']}"):
                                    try:
                                        # Get path context for LLM
                                        path_parts = record['path'].split(" → ")
                                        root_label = path_parts[0] if path_parts else ""
                                        nodes = path_parts[1:6] if len(path_parts) > 1 else []
                                        
                                        # Pad to exactly 5 nodes
                                        while len(nodes) < 5:
                                            nodes.append("")
                                        
                                        llm_response = requests.post(
                                            f"{st.session_state.get('api_base', 'http://localhost:8000')}/llm/fill-triage-actions",
                                            json={
                                                "root": root_label,
                                                "nodes": nodes[:5],
                                                "triage_style": "clinical",
                                                "actions_style": "practical"
                                            }
                                        )
                                        
                                        if llm_response.status_code == 200:
                                            llm_data = llm_response.json()
                                            st.session_state[f"llm_triage_{record['node_id']}"] = llm_data.get("diagnostic_triage", "")
                                            st.session_state[f"llm_actions_{record['node_id']}"] = llm_data.get("actions", "")
                                            st.success("🤖 LLM suggestions loaded!")
                                            st.info(llm_data.get("note", ""))
                                        else:
                                            st.error(f"LLM fill failed: {llm_response.text}")
                                            
                                    except Exception as e:
                                        st.error(f"LLM fill error: {str(e)}")
                            
                            # Inline editing for leaf nodes
                            st.subheader("✏️ Edit Triage (Leaf Only)")
                            
                            # Get LLM suggestions if available
                            llm_triage = st.session_state.get(f"llm_triage_{record['node_id']}", "")
                            llm_actions = st.session_state.get(f"llm_actions_{record['node_id']}", "")
                            
                            if llm_triage or llm_actions:
                                st.info("🤖 LLM suggestions available (review before saving)")
                            
                            diagnostic_triage = st.text_area(
                                "Diagnostic Triage",
                                value=llm_triage or record['diagnostic_triage'] or "",
                                key=f"triage_{record['node_id']}",
                                help="Clinical assessment and triage decision"
                            )
                            
                            actions = st.text_area(
                                "Actions",
                                value=llm_actions or record['actions'] or "",
                                key=f"actions_{record['node_id']}",
                                help="Recommended actions to take"
                            )
                            
                            if st.button(f"💾 Save Changes", key=f"save_{record['node_id']}"):
                                try:
                                    response = put_json(
                                        f"/triage/{record['node_id']}",
                                        {
                                            "diagnostic_triage": diagnostic_triage,
                                            "actions": actions
                                        }
                                    )
                                    st.success("✅ Triage updated successfully!")
                                    
                                    # Clear LLM suggestions after save
                                    if f"llm_triage_{record['node_id']}" in st.session_state:
                                        del st.session_state[f"llm_triage_{record['node_id']}"]
                                    if f"llm_actions_{record['node_id']}" in st.session_state:
                                        del st.session_state[f"llm_actions_{record['node_id']}"]
                                        
                                except Exception as e:
                                    st.error(f"Failed to update triage: {str(e)}")
                        else:
                            st.warning("⚠️ Non-leaf nodes cannot have triage data")
                            st.info("Only leaf nodes (depth 5) can be edited")
                    
                    # Display current triage data
                    st.subheader("📋 Current Triage Data")
                    st.write(f"**Diagnostic Triage:** {record['diagnostic_triage'] or 'Not set'}")
                    st.write(f"**Actions:** {record['actions'] or 'Not set'}")
                    
        else:
            st.info("No triage records found matching the criteria")
            
    except Exception as e:
        st.error(f"Failed to search triage records: {str(e)}")

# Safety notice
if llm_enabled:
    st.divider()
    st.warning("⚠️ **AI Safety Notice:** AI suggestions are guidance-only; dosing and diagnosis are refused. Always review and validate before saving.")
