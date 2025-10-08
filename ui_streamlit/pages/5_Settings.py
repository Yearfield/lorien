from __future__ import annotations

import os

import streamlit as st

from ui_streamlit.api_client import health_json

st.set_page_config(page_title="Settings - Lorien", page_icon="⚙️", layout="wide")

st.title("⚙️ Settings")
st.caption("Configure API connection and application settings")

# Navigation
if st.button("🏠 Home", use_container_width=True):
    st.switch_page("Home.py")

# API Configuration
st.header("🔌 API Configuration")

# Initialize API Base URL in session state
if "API_BASE_URL" not in st.session_state:
    st.session_state["API_BASE_URL"] = os.getenv("LORIEN_API_BASE", "http://127.0.0.1:8000/api/v1")

# API Base URL input
api_base_url = st.text_input(
    "API Base URL",
    value=st.session_state["API_BASE_URL"],
    help="Base URL for the Lorien API (e.g., http://localhost:8000/api/v1)",
)

if api_base_url != st.session_state["API_BASE_URL"]:
    st.session_state["API_BASE_URL"] = api_base_url
    st.success("API Base URL updated")

# Test Connection
st.subheader("🧪 Test Connection")
if st.button("Test Connection", type="primary"):
    try:
        health_data, status_code, tested_url = health_json(timeout=5)

        if health_data and status_code == 200:
            st.success(f"✅ Health 200 OK: {tested_url}")

            # Show full response in code block
            st.code(f"Response from {tested_url}:\n{st.json(health_data)}")

            # Show key metrics
            if health_data.get("version"):
                st.metric("API Version", health_data["version"])
            if health_data.get("db", {}).get("foreign_keys"):
                st.metric("Database", "Connected")

        else:
            st.error(f"❌ Connection Failed: {tested_url}")
            if status_code > 0:
                st.error(f"HTTP Status: {status_code}")

    except Exception as e:
        st.error(f"❌ Connection Error: {str(e)[:100]}...")
        st.caption(f"Tested URL: {st.session_state['API_BASE_URL']}/health")

# Connection Status
st.subheader("📊 Connection Status")
try:
    health_data, status_code, tested_url = health_json(timeout=3)
    if health_data and status_code == 200:
        st.success(f"✅ Connected to: {tested_url}")
        if health_data.get("version"):
            st.caption(f"API Version: {health_data['version']}")
    else:
        st.error(f"❌ Disconnected from: {tested_url}")
        if status_code > 0:
            st.caption(f"HTTP Status: {status_code}")
except Exception as e:
    st.error(f"❌ Connection Error: {str(e)[:100]}...")

# Platform-specific tips
st.header("💡 Platform Tips")

platform_tips = {
    "Android Emulator": "Use `http://10.0.2.2:8000/api/v1` (10.0.2.2 routes to host localhost)",
    "iOS Simulator": "Use `http://localhost:8000/api/v1` (localhost works on iOS sim)",
    "Physical Device": "Use `http://<your-LAN-IP>:8000/api/v1` (e.g., 192.168.1.100:8000)",
    "Web Browser": "Use `http://localhost:8000/api/v1` or your server's public IP",
    "WSL2": "Use `http://localhost:8000/api/v1` (WSL2 forwards localhost to Windows)",
}

for platform, tip in platform_tips.items():
    with st.expander(f"📱 {platform}"):
        st.info(tip)

# Environment Information
st.header("🌍 Environment")
col1, col2 = st.columns(2)

with col1:
    st.write("**Current Environment:**")
    st.code(f"API_BASE_URL: {st.session_state.get('API_BASE_URL', 'Not set')}")
    st.code(f"LORIEN_API_BASE: {os.getenv('LORIEN_API_BASE', 'Not set')}")

with col2:
    st.write("**Common Settings:**")
    st.code("CORS_ALLOW_ALL=true  # For LAN access")
    st.code("DB_PATH=./storage/lorien.db")
    st.code("LLM_ENABLED=false  # Default: OFF")

# Help
st.header("❓ Help")
st.markdown(
    """
**Troubleshooting:**
1. **Connection Failed**: Check if API server is running (`uvicorn api.main:app --reload --port 8000`)
2. **CORS Issues**: Set `CORS_ALLOW_ALL=true` in your environment
3. **Port Conflicts**: Ensure port 8000 is available
4. **Network Issues**: For devices, check firewall and network configuration

**Quick Start:**
1. Start the API server
2. Set the correct API Base URL above
3. Test the connection
4. Navigate to other pages to use the app
"""
)
