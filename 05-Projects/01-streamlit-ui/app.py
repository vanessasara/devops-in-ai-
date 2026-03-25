import asyncio
import streamlit as st
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from src.agents import LogAnalyzerAgent
from src.config import Config

st.set_page_config(
    page_title="AI Log Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "agent" not in st.session_state:
        try:
            Config.validate()
            st.session_state.agent = LogAnalyzerAgent()
        except ValueError as e:
            st.error(f"Configuration error: {e}")
            st.stop()

def display_sidebar():
    with st.sidebar:
        st.title("🔍 AI Log Analyzer")
        st.caption("Agents SDK · LiteLLM · Gemini")
        st.markdown("---")

        st.subheader("Try asking")
        examples = [
            "What log files are available?",
            "Read sample_app.log",
            "Search for ERROR in sample_app.log",
            "Summarise everything and save it",
        ]
        for q in examples:
            if st.button(q, use_container_width=True):
                st.session_state.pending_input = q

        st.markdown("---")

        if st.button("🗑️ Clear chat history", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.caption(f"Model: `{Config.GEMINI_MODEL}`")
        st.caption(f"Logs: `{Config.LOG_DIRECTORY}`")

def display_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

async def get_response(user_input: str) -> str:
    return await st.session_state.agent.process_query(user_input)

def handle_input(user_input: str):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        with st.spinner("Analysing..."):
            response = asyncio.run(get_response(user_input))
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

def main():
    initialize_session_state()
    display_sidebar()

    st.title("💬 Chat with your logs")
    st.markdown("Ask me anything about your log files in plain language.")

    display_messages()

    if "pending_input" in st.session_state and st.session_state.pending_input:
        pending = st.session_state.pending_input
        st.session_state.pending_input = None
        handle_input(pending)

    if prompt := st.chat_input("Ask about your logs..."):
        handle_input(prompt)

if __name__ == "__main__":
    main()