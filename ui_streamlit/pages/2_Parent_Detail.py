from __future__ import annotations
import streamlit as st
import requests
import json
from ui_streamlit.components import top_health_banner, error_message
from ui_streamlit.api_client import get_children, upsert_children
from ui_streamlit.settings import get_api_base_url

st.set_page_config(page_title="Parent Detail", layout="wide")
st.title("Parent Detail")

top_health_banner()

parent_id = st.number_input("Parent ID", min_value=1, step=1, value=int(st.session_state.get("last_incomplete_parent", 1)))
if st.button("Load children"):
    st.session_state["children"] = get_children(parent_id)

children = st.session_state.get("children", [])
if children:
    st.subheader("Slots 1..5")
    edits: list[dict] = []
    for slot in range(1, 6):
        with st.container():
            col_a, col_b = st.columns([3,1])
            curr = next((c for c in children if c.get("slot")==slot), None)
            label = col_a.text_input(f"Slot {slot}", value=(curr.get("label") if curr else ""), key=f"slot_{slot}")
            if label.strip():
                edits.append({"slot": slot, "label": label.strip()})
    if st.button("Save slots", type="primary"):
        try:
            resp = upsert_children(parent_id, edits)
            st.success("Saved")
            st.session_state["children"] = get_children(parent_id)
        except Exception as e:
            error_message(e)
else:
    st.info("Load a parent to edit its slots.")

# LLM Integration Section
st.subheader("Suggest Triage & Actions (LLM)")
st.info("This feature requires LLM_ENABLED=true and a valid model path.")

# Check if LLM is available
try:
    base = get_api_base_url()
    health_response = requests.get(f"{base}/api/v1/health", timeout=10)
    if health_response.status_code == 200:
        health_data = health_response.json()
        llm_enabled = health_data.get("features", {}).get("llm", False)
        
        if llm_enabled:
            st.success("LLM is enabled and available")
            
            # Build path data from current parent/children if available
            if children:
                root_label = st.text_input("Root symptom/label", value="", key="root_label")
                node_labels = []
                for slot in range(1, 6):
                    curr = next((c for c in children if c.get("slot")==slot), None)
                    node_labels.append(curr.get("label", "") if curr else "")
                
                col1, col2 = st.columns(2)
                with col1:
                    triage_style = st.selectbox("Triage style", ["diagnosis-only","short-explanation","none"], index=0)
                with col2:
                    actions_style = st.selectbox("Actions style", ["referral-only","steps","none"], index=0)
                
                apply_now = st.checkbox("Apply immediately to this leaf", value=False)
                
                if st.button("Suggest with LLM", type="secondary"):
                    if not root_label.strip():
                        st.error("Please enter a root symptom/label")
                    else:
                        with st.spinner("Generating LLM suggestion..."):
                            try:
                                payload = {
                                    "root": root_label.strip(),
                                    "nodes": [label.strip() for label in node_labels if label.strip()],
                                    "triage_style": triage_style,
                                    "actions_style": actions_style,
                                    "apply": apply_now,
                                    "node_id": None  # Would need to be set if applying
                                }
                                
                                response = requests.post(
                                    f"{base}/api/v1/llm/fill-triage-actions", 
                                    json=payload, 
                                    timeout=60
                                )
                                
                                if response.status_code == 200:
                                    data = response.json()
                                    st.success("LLM suggestion ready")
                                    st.json(data)
                                else:
                                    st.error(f"LLM error: {response.text}")
                            except Exception as e:
                                st.error(f"Request failed: {str(e)}")
            else:
                st.info("Load children first to use LLM suggestions")
        else:
            st.warning("LLM is not enabled. Set LLM_ENABLED=true and provide a valid model path.")
    else:
        st.error("Could not check API health")
except Exception as e:
    st.error(f"Could not connect to API: {str(e)}")
