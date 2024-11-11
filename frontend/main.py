import streamlit as st
from datetime import datetime
from api import AgentMode, make_agent_api_call
import PyPDF2


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "mode" not in st.session_state:
        st.session_state.mode = AgentMode.WEB_SEARCH
    if "api_error" not in st.session_state:
        st.session_state.api_error = None
    if "pdf_text" not in st.session_state:
        st.session_state.pdf_text = None


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


def extract_text_from_pdf(pdf_file):
    """Convert uploaded PDF to text"""
    try:
        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Extract text from all pages
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        return text.strip()
    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None


def handle_file_upload():
    """Handle PDF file upload in the sidebar"""
    uploaded_file = st.sidebar.file_uploader("Upload PDF for analysis", type=["pdf"])

    if uploaded_file is not None:
        # Convert PDF to text
        pdf_text = extract_text_from_pdf(uploaded_file)

        if pdf_text:
            st.session_state.pdf_text = pdf_text
            st.sidebar.success(
                f"PDF processed successfully! ({len(pdf_text)} characters)"
            )

            # Preview text button
            if st.sidebar.button("Preview Extracted Text"):
                with st.sidebar.expander("Extracted Text"):
                    st.text(pdf_text[:500] + "..." if len(pdf_text) > 500 else pdf_text)

        # Clear PDF button
        if st.sidebar.button("Clear PDF"):
            st.session_state.pdf_text = None
            st.rerun()


def handle_user_input():
    # Get the input prompt
    prompt = st.chat_input("What's on your mind?")

    if prompt:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # If in Future Analysis mode and PDF is uploaded, append the PDF text to prompt
        if (
            st.session_state.mode == AgentMode.FUTURE_ANALYSIS
            and st.session_state.pdf_text
        ):
            full_prompt = f"""
Analysis Request: {prompt}

Document Text:
{st.session_state.pdf_text}
"""
        else:
            full_prompt = prompt

        # Add user message to chat history
        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt,  # Show original prompt in chat
                "metadata": {"mode": st.session_state.mode, "timestamp": timestamp},
            }
        )

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            if (
                st.session_state.mode == AgentMode.FUTURE_ANALYSIS
                and st.session_state.pdf_text
            ):
                st.caption("(Analysis request includes uploaded PDF content)")
            st.caption(f"Mode: {st.session_state.mode.value} | Time: {timestamp}")

        print("full prompt: ", full_prompt)

        # Show a spinner while waiting for API response
        with st.spinner(f"Processing with {st.session_state.mode.value}..."):
            formatted_response = make_agent_api_call(st.session_state.mode, full_prompt)

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

        # Show PDF upload only in Future Analysis mode
        if st.session_state.mode == AgentMode.FUTURE_ANALYSIS:
            st.markdown("---")
            st.markdown("### PDF Analysis")
            handle_file_upload()

            # Show PDF status
            if st.session_state.pdf_text:
                st.info("PDF loaded and ready for analysis")

        st.markdown("---")

        # Clear Chat Button
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.session_state.api_error = None
            st.rerun()

        # Add explanatory text
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
