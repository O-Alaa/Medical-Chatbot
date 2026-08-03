import streamlit as st


# This must be the first Streamlit command.
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
    """
    Initialize values that must persist during the browser session.

    uploaded_documents is still required internally by the uploader,
    even though it is no longer displayed as a page metric.
    """

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = []


def render_header() -> None:
    """Render the title, disclaimer, and conversation statistics."""

    st.title("🚑 Medical Assistant Chatbot")

    st.caption(
        "Ask questions based on the medical documents stored "
        "in the application's knowledge base."
    )

    st.info(
        "This assistant provides educational information from medical "
        "documents. It does not provide diagnoses or replace professional "
        "medical care.",
        icon="🚑",
    )

    # Count only user messages.
    question_count = sum(
        1
        for message in st.session_state.messages
        if message.get("role") == "user"
    )

    # Count only successful assistant answers.
    answer_count = sum(
        1
        for message in st.session_state.messages
        if message.get("role") == "assistant"
    )

    total_messages = len(st.session_state.messages)

    first_column, second_column, third_column = st.columns(3)

    with first_column:
        st.metric(
            label="Questions Asked",
            value=question_count,
        )

    with second_column:
        st.metric(
            label="Answers Generated",
            value=answer_count,
        )

    with third_column:
        st.metric(
            label="Conversation Messages",
            value=total_messages,
        )

    st.divider()


def main() -> None:
    """Run the Streamlit frontend."""

    initialize_session_state()

    # Sidebar components
    render_uploader()
    render_history_download()

    # Main-page components
    render_header()
    render_chat()


if __name__ == "__main__":
    main()
