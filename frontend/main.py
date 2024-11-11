import streamlit as st
from datetime import datetime
from api import AgentMode, make_agent_api_call


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "mode" not in st.session_state:
        st.session_state.mode = AgentMode.WEB_SEARCH
    if "api_error" not in st.session_state:
        st.session_state.api_error = None


def display_chat_history():
    # Display any API errors at the top if they exist
    if st.session_state.api_error:
        st.error(st.session_state.api_error)
        if st.button("Clear Error"):
            st.session_state.api_error = None
            st.rerun()

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

        # Show a spinner while waiting for API response
        with st.spinner(f"Processing with {st.session_state.mode.value}..."):
            # Get response from API based on current mode
            formatted_response = make_agent_api_call(st.session_state.mode, prompt)

        # print(f"hello from response in st {arxiv_list_response}")

        # Add assistant response to chat history
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": formatted_response,
                "metadata": {"mode": st.session_state.mode, "timestamp": timestamp},
            }
        )

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(formatted_response)
            st.caption(f"Mode: {st.session_state.mode.value} | Time: {timestamp}")


def create_sidebar():
    with st.sidebar:
        st.title("Chat Settings")

        # Mode Selection
        st.session_state.mode = st.radio(
            label="Select Chat Mode",
            options=list(AgentMode),
            index=1,
            format_func=lambda mode: mode.value,
            help="Choose the type of interaction you want",
        )

        # Clear Chat Button
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.session_state.api_error = None
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

        *Note: Make sure the FastAPI backend is running on the correct port.*
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
