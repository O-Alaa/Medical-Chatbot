import streamlit as st


# This must be the first Streamlit command in the application.
st.set_page_config(
    page_title="Medical Assistant Chatbot",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded",
)


from components.chatUI import render_chat
from components.history_download import render_history_download
from components.upload import render_uploader


def initialize_session_state() -> None:
    """Initialize values that should persist during the user session."""

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = []


def render_header() -> None:
    """Render the main application heading and statistics."""

    st.title("🚑 Medical Assistant Chatbot")
    st.caption(
        "Ask questions based on your uploaded medical documents."
    )

    st.info(
        "This assistant provides educational information from uploaded "
        "documents. It does not provide diagnoses or replace professional "
        "medical care.",
        icon="ℹ️",
    )

    document_count = len(st.session_state.uploaded_documents)

    question_count = sum(
        1
        for message in st.session_state.messages
        if message.get("role") == "user"
    )

    answer_count = sum(
        1
        for message in st.session_state.messages
        if message.get("role") == "assistant"
    )

    first_column, second_column, third_column = st.columns(3)

    with first_column:
        st.metric(
            label="Session Documents",
            value=document_count,
        )

    with second_column:
        st.metric(
            label="Questions Asked",
            value=question_count,
        )

    with third_column:
        st.metric(
            label="Answers Generated",
            value=answer_count,
        )

    st.divider()


def main() -> None:
    """Run the Streamlit frontend."""

    initialize_session_state()

    # Sidebar components
    render_uploader()
    render_history_download()

    # Main page components
    render_header()
    render_chat()


if __name__ == "__main__":
    main()
