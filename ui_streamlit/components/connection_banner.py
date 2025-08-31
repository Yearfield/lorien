import streamlit as st
from ui_streamlit.api_client import health_json

def render_connection_banner():
    """Render connection status banner using /health endpoint only"""
    try:
        health_data, status_code, tested_url = health_json(timeout=3)
        
        if health_data and status_code == 200:
            st.session_state["CONNECTED"] = True
            st.session_state["HEALTH_JSON"] = health_data
            
            # Show success with URL
            st.success(f"✅ API Connected: {tested_url}")
            
            # Show version info if available
            if health_data.get("version"):
                st.caption(f"Version: {health_data['version']}")
                
        else:
            st.session_state["CONNECTED"] = False
            st.session_state["HEALTH_JSON"] = None
            
            # Show error with tested URL
            st.error(f"❌ API Disconnected: {tested_url}")
            if status_code > 0:
                st.caption(f"HTTP Status: {status_code}")
                
    except Exception as e:
        st.session_state["CONNECTED"] = False
        st.session_state["HEALTH_JSON"] = None
        
        # Show error with fallback URL
        base_url = st.session_state.get("API_BASE_URL", "http://localhost:8000")
        st.error(f"❌ Connection Error: {base_url}/health")
        st.caption(f"Error: {str(e)[:100]}...")
