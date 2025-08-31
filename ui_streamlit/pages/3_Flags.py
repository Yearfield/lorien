from __future__ import annotations
import streamlit as st
from ui_streamlit.components import top_health_banner, error_message
from ui_streamlit.api_client import get_json, post_json, delete_json

st.set_page_config(
    page_title="Flags - Lorien",
    page_icon="🚩",
    layout="wide"
)

st.title("🚩 Red Flag Management")
st.caption("Assign and manage red flags across decision tree nodes")

# Navigation
if st.button("🏠 Home", use_container_width=True):
    st.switch_page("Home.py")

# Search flags
st.header("🔍 Search Flags")
search_query = st.text_input("Search flags by name or description", placeholder="e.g., urgent, critical, emergency")

try:
    if search_query:
        results = get_json(f"/flags/search?query={search_query}")
    else:
        results = get_json("/flags/search")
    
    if not results:
        st.info("🚩 No flags defined — import or add via Flags admin.")
        st.markdown("""
        **To get started with flags:**
        1. **Import Data**: Use Workspace to import Excel workbooks with flag definitions
        2. **Create Flags**: Add new red flags through the API or admin interface
        3. **Assign Flags**: Use the assignment tools below once flags are available
        4. **Track Usage**: Monitor flag assignments and removals in the audit log
        """)
        st.stop()
    
    st.success(f"Found {len(results)} flags")
    
    # Display flags
    for flag in results:
        with st.expander(f"🚩 {flag.get('name', 'No name')}"):
            st.write(f"**Description:** {flag.get('description', 'No description')}")
            st.write(f"**Severity:** {flag.get('severity', 'Unknown')}")
            st.write(f"**Flag ID:** {flag.get('id', 'Unknown')}")
            
            # Assignment section
            st.subheader("📋 Assignment")
            node_id = st.text_input(f"Node ID to assign {flag.get('name', 'flag')} to", key=f"node_{flag['id']}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Assign to Node", key=f"assign_{flag['id']}"):
                    if node_id:
                        try:
                            result = post_json(f"/flags/{flag['id']}/assign", {"node_id": int(node_id)})
                            st.success(f"Flag {flag.get('name', 'flag')} assigned to node {node_id}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error assigning flag: {str(e)[:100]}...")
                    else:
                        st.warning("Please enter a node ID")
            
            with col2:
                if st.button(f"❌ Remove from Node", key=f"remove_{flag['id']}"):
                    if node_id:
                        try:
                            result = delete_json(f"/flags/{flag['id']}/assign/{node_id}")
                            st.success(f"Flag {flag.get('name', 'flag')} removed from node {node_id}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error removing flag: {str(e)[:100]}...")
                    else:
                        st.warning("Please enter a node ID")
    
    # Bulk operations
    st.header("📦 Bulk Operations")
    st.info("Bulk operations will be available in future updates")
    
except Exception as e:
    st.error(f"Error loading flags: {str(e)[:100]}...")
    st.info("Please check your API connection in Settings")

# Flag audit
st.header("📊 Flag Audit")
try:
    audit_entries = get_json("/flags/audit?limit=20")
    
    if audit_entries:
        st.write(f"Recent flag operations: {len(audit_entries)} entries")
        
        for entry in audit_entries[:10]:  # Show first 10
            with st.expander(f"{entry.get('action', 'Unknown')} - {entry.get('flag_name', 'Unknown flag')}"):
                st.write(f"**Node ID:** {entry.get('node_id', 'Unknown')}")
                st.write(f"**Action:** {entry.get('action', 'Unknown')}")
                st.write(f"**Timestamp:** {entry.get('timestamp', 'Unknown')}")
                st.write(f"**User:** {entry.get('user_id', 'System')}")
    else:
        st.info("📊 No audit entries found")
        
except Exception as e:
    st.warning(f"⚠️ Could not load audit entries: {str(e)[:100]}...")

# Help section
st.header("❓ Flags Help")
st.markdown("""
**Red Flag System:**
- 🚩 **Flags** mark critical decision points or urgent conditions
- **Assignment** links flags to specific tree nodes
- **Audit** tracks all flag operations for compliance
- **Bulk Operations** allow mass flag management

**Common Use Cases:**
1. **Urgent Symptoms**: Mark nodes requiring immediate attention
2. **Critical Paths**: Flag high-risk decision branches
3. **Quality Gates**: Ensure required assessments are completed
4. **Compliance**: Track mandatory clinical protocols

**Best Practices:**
- Use descriptive flag names and descriptions
- Assign appropriate severity levels
- Review audit logs regularly
- Remove flags when no longer relevant
""")
