from typing import List, Union
import streamlit as st
from datetime import datetime
from enum import Enum
import requests

# Define the base URL for your FastAPI backend
API_BASE_URL = "http://localhost:8000"  # Adjust this to match your FastAPI server


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
    if "api_error" not in st.session_state:
        st.session_state.api_error = None


def make_agent_api_call(mode: AgentMode, prompt: str) -> Union[List[dict], str]:
    """
    Make API calls to different endpoints based on the selected mode
    """
    # Define endpoints for each mode
    endpoints = {
        AgentMode.AUTO_AGENT: "/api/auto-agent",
        AgentMode.WEB_SEARCH: "/api/web-search",
        AgentMode.DB_QUERY: "/api/db-query",
        AgentMode.QA_MODE: "/api/qa",
        AgentMode.FUTURE_ANALYSIS: "/api/future-analysis",
    }

    endpoint = endpoints[mode]

    try:
        response = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json={"prompt": prompt, "max_results": 5},
            headers={"Content-Type": "application/json"},
            timeout=30,  # Timeout after 30 seconds
        )
        response.raise_for_status()
        print("hello from response in st", response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        st.session_state.api_error = f"API Error: {str(e)}"
        return f"Error processing request. Please try again later. ({str(e)})"


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


def format_arxiv_results(results: List[dict]) -> str:
    """
    Format arxiv results into a nice markdown list with expandable details
    """
    formatted_output = []

    for idx, paper in enumerate(results, 1):
        # Create the main list item with title and summary
        title = paper.get("title", "Untitled")
        authors = ", ".join(
            [author.get("name", "") for author in paper.get("authors", [])]
        )
        summary = paper.get("summary", "").replace("\n", " ")

        # Create details section
        details = f"""
- **Authors:** {authors}
- **Published:** {paper.get('published', 'N/A')}
- **Categories:** {', '.join(paper.get('categories', []))}
- **Paper URL:** [{paper.get('entry_id', 'N/A')}]({paper.get('entry_id', '#')})
- **PDF URL:** [{paper.get('pdf_url', 'N/A')}]({paper.get('pdf_url', '#')})

**Abstract:**
{summary}
"""
        # Combine the main list item with the details
        formatted_item = f"{idx}. **{title}**\n{details}\n"
        formatted_output.append(formatted_item)

    return "\n".join(formatted_output)


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
            arxiv_list_response = make_agent_api_call(st.session_state.mode, prompt)

        # print(f"hello from response in st {arxiv_list_response}")

        # Format the response if it's a list of arxiv results
        if isinstance(arxiv_list_response, list) and arxiv_list_response:
            formatted_response = format_arxiv_results(arxiv_list_response)
        else:
            formatted_response = str(arxiv_list_response)

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
