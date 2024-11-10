import streamlit as st


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []


def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def handle_user_input():
    if prompt := st.chat_input("What's on your mind?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Here you would typically call your LLM
        # For now, we'll just echo the message back
        response = f"Echo: {prompt}"

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(response)


def main():
    st.title("Attensions_Sight Chat Interface")

    # Initialize session state for storing chat history
    initialize_session_state()

    # Display chat history
    display_chat_history()

    # Handle user input
    handle_user_input()


if __name__ == "__main__":
    main()
