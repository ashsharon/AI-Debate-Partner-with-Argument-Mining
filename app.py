"""
app.py
------
Streamlit frontend for the AI Debate Partner with Argument Mining.

Run with: streamlit run app.py
"""

import json
import os
import streamlit as st
from pipeline import DebateSession

st.set_page_config(page_title="AI Debate Partner", page_icon="⚖️", layout="centered")

st.title("⚖️ AI Debate Partner")
st.caption("Debate an AI that always argues the opposing side - and watch the argument "
           "structure build as a graph in real time.")

with st.sidebar:
    st.header("About")
    st.write(
        "Most debate bots just generate text. This tool mines the STRUCTURE of each "
        "argument (claim, warrant, stance) as the debate happens, and visualizes it as "
        "a graph of who is rebutting whom."
    )

here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "data", "sample_topics.json")) as f:
    sample_topics = json.load(f)

if "session" not in st.session_state:
    st.session_state["session"] = None
    st.session_state["chat_log"] = []

if st.session_state["session"] is None:
    st.subheader("Choose a debate topic")
    topic_choice = st.selectbox("Pick a sample topic, or write your own below:", ["(write my own)"] + sample_topics)
    custom_topic = st.text_input("Or enter a custom topic:") if topic_choice == "(write my own)" else ""

    if st.button("Start Debate", type="primary"):
        final_topic = custom_topic.strip() if topic_choice == "(write my own)" else topic_choice
        if not final_topic:
            st.warning("Please choose or enter a topic.")
        else:
            st.session_state["session"] = DebateSession(final_topic)
            st.session_state["chat_log"] = []
            st.rerun()
else:
    session = st.session_state["session"]
    st.subheader(f"Topic: {session.topic}")

    if st.button("Start a new debate"):
        st.session_state["session"] = None
        st.session_state["chat_log"] = []
        st.rerun()

    for turn in st.session_state["chat_log"]:
        with st.chat_message(turn["role"]):
            st.write(turn["content"])

    user_input = st.chat_input("Make your argument...")
    if user_input:
        st.session_state["chat_log"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.spinner("Thinking of a counterargument..."):
            result = session.submit_user_turn(user_input)

        st.session_state["chat_log"].append({"role": "assistant", "content": result["ai_reply"]})
        with st.chat_message("assistant"):
            st.write(result["ai_reply"])

        st.session_state["latest_graph"] = result["graph_dot"]

    if st.session_state.get("latest_graph"):
        st.divider()
        st.subheader("Argument Structure Graph")
        st.caption("Blue = supports the topic, red = opposes the topic. Arrows show which claim rebuts which.")
        st.graphviz_chart(st.session_state["latest_graph"])
