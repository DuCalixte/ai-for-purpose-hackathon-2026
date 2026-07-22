import os
import sys

# Forces the parent folder into the path system
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import plotly.io as pio
from auth import validate_key

st.set_page_config(layout="wide")

if "auth" not in st.session_state: 
    st.session_state.auth = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "active_view" not in st.session_state:
    st.session_state.active_view = "chat"

with st.sidebar:
    key = st.text_input("API Key", type="password")
    if st.button("Connect"): 
        st.session_state.auth = validate_key(key)
    
    if st.session_state.auth:
        st.markdown("---")
        st.markdown("### View Controls")
        
        has_table = False
        has_graph = False
        
        if st.session_state.messages:
            last_assistant_msg = next((m for m in reversed(st.session_state.messages) if m["role"] == "assistant" and "result" in m), None)
            if last_assistant_msg:
                res = last_assistant_msg["result"]
                has_table = "table" in res and res["table"] is not None
                has_graph = "graph" in res and res["graph"] is not None

        if st.button("Show Chat View", use_container_width=True):
            st.session_state.active_view = "chat"
            
        if st.button("View Table", disabled=not has_table, use_container_width=True):
            st.session_state.active_view = "table"
            
        if st.button("View Graph", disabled=not has_graph, use_container_width=True):
            st.session_state.active_view = "graph"

if st.session_state.auth:
    # 1. Render content view structure
    if st.session_state.active_view == "chat":
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
    elif st.session_state.active_view == "table":
        last_assistant_msg = next((m for m in reversed(st.session_state.messages) if m["role"] == "assistant" and "result" in m), None)
        if last_assistant_msg and last_assistant_msg["result"]["table"] is not None:
            st.dataframe(last_assistant_msg["result"]["table"], use_container_width=True)
            
    elif st.session_state.active_view == "graph":
        last_assistant_msg = next((m for m in reversed(st.session_state.messages) if m["role"] == "assistant" and "result" in m), None)
        if last_assistant_msg and last_assistant_msg["result"]["graph"] is not None:
            st.plotly_chart(last_assistant_msg["result"]["graph"], use_container_width=True)

    # 2. Handle new user input and API communication with processing layout spinner
    if prompt := st.chat_input("Ask about reimbursement..."):
        with st.chat_message("user"):
            st.write(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        url = "http://0.0.0.0:8000/api/v1/chat"
        payload = {"query": prompt}
        headers = {
            "x-api-key": key,
            "Content-Type": "application/json"
        }
        
        # Enclose API execution inside a visible workspace spinner status wrapper
        with st.spinner("Processing request..."):
            try:
                response = requests.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    agent_response_text = data.get("response", "")
                    
                    table_data = data.get("table")
                    df = pd.DataFrame(table_data) if table_data else None
                    
                    graph_data = data.get("graph")
                    fig = pio.from_json(graph_data) if graph_data else None
                    
                    agent_result_data = {"table": df, "graph": fig}
                    
                    if df is not None:
                        st.session_state.active_view = "table"
                    elif fig is not None:
                        st.session_state.active_view = "graph"
                    else:
                        st.session_state.active_view = "chat"
                else:
                    agent_response_text = f"Error: Server responded with status code {response.status_code}."
                    agent_result_data = {"table": None, "graph": None}
                    st.session_state.active_view = "chat"
                    
            except requests.exceptions.RequestException as e:
                agent_response_text = f"Failed to connect to the backend server: {str(e)}"
                agent_result_data = {"table": None, "graph": None}
                st.session_state.active_view = "chat"
        
        msg_id = len(st.session_state.messages)
        st.session_state.messages.append({
            "id": msg_id,
            "role": "assistant", 
            "content": agent_response_text,
            "result": agent_result_data
        })
        st.rerun()
