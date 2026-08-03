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
    """Render one chat message without displaying document sources."""

    role = message.get("role", "assistant")
    content = message.get("content", "")

    avatar = "👤" if role == "user" else "🩺"

    with st.chat_message(role, avatar=avatar):
        st.markdown(content)


def render_welcome_section() -> str | None:
    """
    Render the welcome area and suggested questions.

    Returns:
        The selected suggested question, or None.
    """

    with st.container(border=True):
        st.subheader("Welcome to your medical knowledge assistant")

        st.write(
            "Ask questions about symptoms, conditions, risk factors, "
            "prevention, and other medical information available in "
            "the application's knowledge base."
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
    """Send the user's question to the backend and display the answer."""

    question = question.strip()

    if not question:
        return

    # Save and display the user's message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    # Request and display the assistant's answer
    with st.chat_message("assistant", avatar="🩺"):
        try:
            with st.spinner("Searching the medical knowledge base..."):
                response_data = ask_question(question)

            answer = response_data.get(
                "response",
                "The backend returned an empty answer.",
            )

            st.markdown(answer)

            # Store only the answer, without source metadata
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
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
                }
            )


def render_chat() -> None:
    """Render the complete chatbot interface."""

    st.subheader("💬 Chat with your medical assistant")

    # Render the existing conversation
    for message in st.session_state.messages:
        render_message(message)

    selected_question = None

    if not st.session_state.messages:
        selected_question = render_welcome_section()

    typed_question = st.chat_input(
        "Ask a question about a medical condition..."
    )

    question = typed_question or selected_question

    if question:
        process_question(question)
