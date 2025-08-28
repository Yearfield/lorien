from __future__ import annotations
import os
import streamlit as st
import requests
import json
from ui_streamlit.components import top_health_banner
from ui_streamlit.settings import get_api_base_url

st.set_page_config(page_title="Settings", layout="wide")
st.title("Settings")

health = top_health_banner()

# API Configuration
st.subheader("API Configuration")
current_base = get_api_base_url()
st.write(f"**Current API Base:** {current_base}")

# API Base URL override (session state)
new_base = st.text_input(
    "Override API Base URL", 
    value=current_base,
    placeholder="http://localhost:8000",
    help="This will be used for the current session only"
)

if new_base != current_base:
    st.session_state["api_base_override"] = new_base
    st.success(f"API base URL updated to: {new_base}")

# Environment info
st.subheader("Environment")
st.write(f"API_BASE_URL env: {os.environ.get('API_BASE_URL')!r}")
st.write(f"LORIEN_API_BASE env: {os.environ.get('LORIEN_API_BASE')!r}")

# LAN Configuration Tips
st.subheader("🌐 LAN Configuration Tips")
st.info("""
**Android Emulator:** `http://10.0.2.2:<port>`  
**Physical Device (same network):** `http://<LAN-IP>:<port>`  
**iOS Simulator:** `http://localhost:<port>`  
**Physical iOS Device (same network):** `http://<LAN-IP>:<port>`
""")

# CORS Configuration
cors_allow_all = os.environ.get("CORS_ALLOW_ALL", "false").lower() == "true"
st.write(f"**CORS Allow All:** {cors_allow_all}")
if cors_allow_all:
    st.success("LAN access enabled - devices can reach the API")
else:
    st.warning("LAN access restricted - set CORS_ALLOW_ALL=true for mobile testing")

# Test Connection
st.subheader("🔗 Test Connection")
if st.button("Ping API"):
    try:
        base_to_test = st.session_state.get("api_base_override", current_base)
        r = requests.get(f"{base_to_test}/health", timeout=5)
        if r.status_code == 200:
            st.success("✅ API connection successful")
            health_data = r.json()
            
            # Display health data
            st.subheader("Health Response")
            st.json(health_data)
            
            # Show key info
            if "version" in health_data:
                st.info(f"**Version:** {health_data['version']}")
            if "db" in health_data and "path" in health_data["db"]:
                st.info(f"**Database Path:** {health_data['db']['path']}")
            if "features" in health_data:
                llm_status = "✅ Enabled" if health_data["features"].get("llm") else "❌ Disabled"
                st.info(f"**LLM:** {llm_status}")
        else:
            st.error(f"❌ API connection failed: {r.status_code}")
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")

# LLM Health Check
st.subheader("🤖 LLM Status")
if st.button("Check LLM Health"):
    try:
        base_to_test = st.session_state.get("api_base_override", current_base)
        r = requests.get(f"{base_to_test}/llm/health", timeout=5)
        if r.status_code == 200:
            st.success("✅ LLM is enabled and available")
            llm_data = r.json()
            st.json(llm_data)
        elif r.status_code == 503:
            st.warning("⚠️ LLM is disabled (returns 503)")
            st.info("Set LLM_ENABLED=true and ensure model file exists to enable LLM features")
        else:
            st.error(f"❌ LLM health check failed: {r.status_code}")
    except Exception as e:
        st.error(f"❌ LLM check error: {str(e)}")

# Configuration Help
st.subheader("📝 Configuration Help")
st.markdown("""
**To change API base URL permanently:**
1. Set environment variable: `export LORIEN_API_BASE="http://your-ip:8000"`
2. Or create `.streamlit/secrets.toml` with: `API_BASE_URL = "http://your-ip:8000"`
3. Restart Streamlit

**For LAN access:**
1. Set `CORS_ALLOW_ALL=true` in your environment
2. Ensure your device is on the same network as the API server
3. Use the LAN IP address of your API server
""")
