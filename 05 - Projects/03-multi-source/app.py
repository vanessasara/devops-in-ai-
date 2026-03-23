import asyncio
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from src.agents import LogAnalyzerAgent
from src.config import Config

st.set_page_config(
    page_title="AI Incident Responder",
    page_icon="🚨",
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
        st.title("🚨 AI Incident Responder")
        st.caption("Agents SDK · LiteLLM · Gemini")
        st.markdown("---")

        st.subheader("Status")
        st.success("Gemini API ✓")
        if Config.K8S_ENABLED:
            st.success("Kubernetes ✓ live mode")
        else:
            st.warning("Kubernetes ⚠ simulation mode")

        st.markdown("---")

        st.subheader("Severity Levels")
        st.markdown("""
- 🔴 **P1** Critical — service down, restart recommended
- 🟠 **P2** High — degraded, investigate immediately
- 🟡 **P3** Medium — warning, monitor and plan
- 🔵 **Info** — no action needed
        """)

        st.markdown("---")

        st.subheader("Try asking")
        examples = [
            "Check k8s-java-app.log for issues",
            "What is the severity of the problem?",
            "What caused the pod to crash?",
            "Search for OOM in k8s-java-app.log",
        ]
        for q in examples:
            if st.button(q, use_container_width=True):
                st.session_state.pending_input = q

        st.markdown("---")

        if st.button("🗑️ Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")
        st.caption(f"Model: `{Config.GEMINI_MODEL}`")
        st.caption(f"K8s: `{'live' if Config.K8S_ENABLED else 'simulation'}`")


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
        with st.spinner("Analysing incident..."):
            response = asyncio.run(get_response(user_input))
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})


def main():
    initialize_session_state()
    display_sidebar()

    st.title("🚨 AI Incident Responder")
    st.markdown(
        "Ask about your logs. The agent will classify severity, "
        "recommend an action, and ask for your approval before doing anything."
    )

    display_messages()

    if "pending_input" in st.session_state and st.session_state.pending_input:
        pending = st.session_state.pending_input
        st.session_state.pending_input = None
        handle_input(pending)

    if prompt := st.chat_input("Describe the issue or ask about your logs..."):
        handle_input(prompt)


if __name__ == "__main__":
    main()
