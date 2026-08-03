from typing import Any

import streamlit as st

from utils.api import APIError, ask_question


SUGGESTED_QUESTIONS = [
    "What are the common symptoms and causes of headaches?",
    "What are the warning signs of a stroke?",
    "What is hypertension and what are its risk factors?",
    "What are the common symptoms of asthma?",
    "What is diabetes and what symptoms can it cause?",
    "What are the symptoms of a chest cold?",
    "What information is available about kidney disease?",
    "What symptoms can occur with allergies or infectious diseases?",
]


def format_source(source: Any) -> str:
    """
    Convert a backend source value into readable text.

    The backend may return a source as a string or dictionary.
    """

    if isinstance(source, dict):
        source_name = (
            source.get("source_file")
            or source.get("source")
            or source.get("file_name")
            or "Unknown document"
        )

        page = source.get("page")

        if page is not None:
            try:
                return f"{source_name} — Page {int(page) + 1}"
            except (TypeError, ValueError):
                return f"{source_name} — Page {page}"

        return str(source_name)

    return str(source).strip()


def normalize_sources(sources: list[Any]) -> list[str]:
    """Remove empty and duplicate source values."""

    normalized_sources = []

    for source in sources:
        formatted_source = format_source(source)

        if (
            formatted_source
            and formatted_source != "Unknown document"
            and formatted_source not in normalized_sources
        ):
            normalized_sources.append(formatted_source)

    return normalized_sources


def render_sources(sources: list[Any]) -> None:
    """Render the source documents used for an answer."""

    normalized_sources = normalize_sources(sources)

    if not normalized_sources:
        return

    with st.expander(
        f"📚 Sources used ({len(normalized_sources)})",
        expanded=False,
    ):
        for source in normalized_sources:
            st.markdown(f"- `{source}`")


def render_message(message: dict) -> None:
    """Render one stored chat message."""

    role = message.get("role", "assistant")
    content = message.get("content", "")
    sources = message.get("sources", [])

    avatar = "👤" if role == "user" else "🩺"

    with st.chat_message(role, avatar=avatar):
        st.markdown(content)

        if role == "assistant":
            render_sources(sources)


def render_welcome_section() -> str | None:
    """
    Render the empty conversation screen.

    Returns the selected suggested question when a button is clicked.
    """

    with st.container(border=True):
        st.subheader("Welcome to your medical knowledge assistant")

        st.write(
            "Upload trusted medical PDFs from the sidebar, then ask questions "
            "about diseases, symptoms, risk factors, prevention, and other "
            "information contained in the documents."
        )

        st.markdown("#### Suggested questions")

        selected_question = None

        first_column, second_column = st.columns(2)

        for index, question in enumerate(SUGGESTED_QUESTIONS):
            target_column = (
                first_column
                if index % 2 == 0
                else second_column
            )

            with target_column:
                if st.button(
                    question,
                    key=f"suggested_question_{index}",
                    use_container_width=True,
                ):
                    selected_question = question

        return selected_question


def process_question(question: str) -> None:
    """Send a question to the backend and display its answer."""

    question = question.strip()

    if not question:
        return

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🩺"):
        try:
            with st.spinner(
                "Searching the medical knowledge base..."
            ):
                response_data = ask_question(question)

            answer = response_data.get("response")

            if not answer:
                answer = (
                    "The backend completed the request but returned "
                    "an empty answer."
                )

            sources = response_data.get("sources", [])

            st.markdown(answer)
            render_sources(sources)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                }
            )

        except APIError as error:
            error_message = (
                "The request could not be completed. "
                f"{error}"
            )

            st.error(error_message)

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": error_message,
                    "sources": [],
                }
            )


def render_chat() -> None:
    """Render the chatbot area."""

    st.subheader("💬 Chat with your medical library")

    # Display previous conversation messages.
    for message in st.session_state.messages:
        render_message(message)

    selected_question = None

    if not st.session_state.messages:
        selected_question = render_welcome_section()

    typed_question = st.chat_input(
        "Ask a question about your medical documents..."
    )

    question = typed_question or selected_question

    if question:
        process_question(question)
