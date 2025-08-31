import streamlit as st
from ui_streamlit.components.connection_banner import render_connection_banner

st.set_page_config(
    page_title="Lorien - Decision Tree Manager",
    page_icon="🌳",
    layout="wide"
)

# Render connection banner at the top
render_connection_banner()

st.title("🌳 Lorien Decision Tree Manager")
st.caption("Cross-platform decision tree management with AI-powered insights")

# Status section
st.header("📊 Status")
if st.session_state.get("CONNECTED"):
    st.success("✅ API Connected")
    if st.session_state.get("HEALTH_JSON"):
        health = st.session_state["HEALTH_JSON"]
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Version", health.get("version", "Unknown"))
        with col2:
            st.metric("Database", "Connected" if health.get("db", {}).get("foreign_keys") else "Error")
else:
    st.error("❌ API Disconnected")
    st.info("Please check your API Base URL in Settings")

# Navigation
st.header("🧭 Navigation")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🏠 Workspace", use_container_width=True):
        st.switch_page("pages/0_Workspace.py")
    if st.button("✏️ Editor", use_container_width=True):
        st.switch_page("pages/1_Editor.py")

with col2:
    if st.button("⚠️ Conflicts", use_container_width=True):
        st.switch_page("pages/1_Conflicts.py")
    if st.button("📋 Outcomes", use_container_width=True):
        st.switch_page("pages/2_Outcomes.py")

with col3:
    if st.button("🧮 Calculator", use_container_width=True):
        st.switch_page("pages/4_Calculator.py")
    if st.button("⚙️ Settings", use_container_width=True):
        st.switch_page("pages/5_Settings.py")

# About section
st.header("ℹ️ About")
st.markdown("""
**Lorien** is a cross-platform decision tree management platform that helps healthcare professionals 
create, manage, and navigate complex diagnostic decision trees.

**Key Features:**
- 🌳 **Tree Management**: Create and edit decision trees with exactly 5 children per parent
- 📊 **Data Import/Export**: Excel and CSV support with validation
- 🚩 **Red Flag Management**: Assign and track critical flags across nodes
- 🤖 **AI Integration**: LLM-powered triage suggestions (when enabled)
- 📱 **Cross-Platform**: Web (Streamlit) and mobile (Flutter) interfaces

**Current Version:** v6.8.0-beta.1
**Target Beta Start:** 2024-12-20
**Target Beta End:** 2024-12-27
""")

# Quick start
st.header("🚀 Quick Start")
st.markdown("""
1. **Check Connection**: Verify API connectivity above
2. **Import Data**: Use Workspace to import Excel workbooks
3. **Edit Trees**: Use Editor to manage parent-child relationships
4. **Resolve Conflicts**: Check Conflicts for data integrity issues
5. **Manage Outcomes**: Use Outcomes for triage and actions
6. **Calculate Paths**: Use Calculator for decision tree navigation
""")
