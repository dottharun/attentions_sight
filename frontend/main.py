import streamlit as st
from datetime import datetime
from enum import Enum


class AgentMode(Enum):
    AUTO_AGENT = "Auto Agent"
    WEB_SEARCH = "Web Search"
    DB_QUERY = "DB Query"
    QA_MODE = "QA Mode"
    FUTURE_ANALYSIS = "Future works/analysis"


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "mode" not in st.session_state:
        st.session_state.mode = AgentMode.WEB_SEARCH


def get_current_mode_response(prompt):
    """
    Simulate different mode responses - replace with actual implementations
    """
    modes = {
        AgentMode.AUTO_AGENT: f"Auto Agent: {prompt}",
        AgentMode.QA_MODE: f"Q&A Agent:: {prompt}",
        AgentMode.WEB_SEARCH: f"Search Agent: {prompt}",
        AgentMode.DB_QUERY: f"Database Agent: {prompt}",
        AgentMode.FUTURE_ANALYSIS: f"Future works Agent: {prompt}",
    }
    return modes[st.session_state.mode]


def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "metadata" in message:
                st.caption(
                    f"Mode: {message['metadata']['mode'].value} | Time: {message['metadata']['timestamp']}"
                )


def handle_user_input():
    if prompt := st.chat_input("What's on your mind?"):
        # Add user message to chat history
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,
                "metadata": {"mode": st.session_state.mode, "timestamp": timestamp},
            }
        )

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"Mode: {st.session_state.mode.value} | Time: {timestamp}")

        # Get response based on current mode
        response = get_current_mode_response(prompt)

        # Add assistant response to chat history
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response,
                "metadata": {"mode": st.session_state.mode, "timestamp": timestamp},
            }
        )

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)
            st.caption(f"Mode: {st.session_state.mode.value} | Time: {timestamp}")


def create_sidebar():
    with st.sidebar:
        st.title("Chat Settings")

        # Mode Selection
        st.session_state.mode = st.radio(
            label="Select Chat Mode",
            options=list(AgentMode),
            index=1,  # to self the default agent mode
            format_func=lambda mode: mode.value,
            help="Choose the type of interaction you want",
        )

        # Clear Chat Button
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

        # Add some explanatory text
        st.markdown("---")
        st.markdown(
            """
        ### Mode Descriptions:
        - **Auto Agent**: Automatic task processing
        - **Web Search**: Search and summarize web content
        - **DB Query**: Query connected databases
        - **QA Mode**: Simple question-answering
        - **Future works/analysis**: Analysis and Future path for the content provided

        *Note: This is a demo. Some features may be simulated.*
        """
        )


def main():
    st.title("🤖 Multi-Agent Chat Interface")

    # Initialize session state
    initialize_session_state()

    # Create sidebar with settings
    create_sidebar()

    # Display current mode
    st.markdown(f"**Current Mode**: {st.session_state.mode.value}")

    # Display chat history
    display_chat_history()

    # Handle user input
    handle_user_input()


if __name__ == "__main__":
    main()
