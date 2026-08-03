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


def render_message(message: dict) -> None:
    """
    Render a single message from the conversation history.

    Args:
        message: Dictionary containing the message role and content.
    """

    role = message.get("role", "assistant")
    content = message.get("content", "")

    avatar = "👤" if role == "user" else "🚑"

    with st.chat_message(role, avatar=avatar):
        st.markdown(content)


def render_welcome_section() -> str | None:
    """
    Render the welcome section and suggested questions.

    Returns:
        The selected suggested question, or None when no question
        has been selected.
    """

    with st.container(border=True):
        st.subheader("Welcome to Medical Assistant Chatbot")

        st.write(
            "Ask questions about symptoms, medical conditions, risk factors, "
            "prevention, and other information available in the medical "
            "knowledge base."
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
    """
    Send the user's question to the backend and display the answer.

    Args:
        question: Medical question entered or selected by the user.
    """

    question = question.strip()

    if not question:
        return

    # Save the user's question in the conversation history.
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    # Display the current user message immediately.
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    # Request an answer from the deployed FastAPI backend.
    with st.chat_message("assistant", avatar="🚑"):
        try:
            with st.spinner(
                "Searching the medical knowledge base..."
            ):
                response_data = ask_question(question)

            answer = response_data.get(
                "response",
                "The backend returned an empty answer.",
            )

            st.markdown(answer)

            # Store only successful assistant answers.
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                }
            )

            # Refresh the application so all counters update immediately.
            st.rerun()

        except APIError as error:
            st.error(
                "The request could not be completed. "
                f"{error}"
            )


def render_chat() -> None:
    """Render the complete Medical Assistant Chatbot interface."""

    st.subheader("💬 Chat with your medical assistant")

    # Display the existing conversation history.
    for message in st.session_state.messages:
        render_message(message)

    selected_question = None

    # Display the welcome section only before the first message.
    if not st.session_state.messages:
        selected_question = render_welcome_section()

    typed_question = st.chat_input(
        "Ask a question about a medical condition..."
    )

    # Accept either a typed question or a suggested-question button.
    question = typed_question or selected_question

    if question:
        process_question(question)
