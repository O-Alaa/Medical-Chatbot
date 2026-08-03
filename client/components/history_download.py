from datetime import datetime
from typing import Any

import streamlit as st


def format_source_for_export(source: Any) -> str:
    """Convert a source value into text for the history file."""

    if isinstance(source, dict):
        source_name = (
            source.get("source_file")
            or source.get("source")
            or source.get("file_name")
            or "Unknown document"
        )

        page = source.get("page")

        if page is not None:
            return f"{source_name} — Page {page}"

        return str(source_name)

    return str(source)


def build_chat_history() -> str:
    """Convert the conversation into plain text."""

    lines = [
        "MediDoc AI — Chat History",
        f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
    ]

    for message in st.session_state.messages:
        role = message.get("role", "assistant").upper()
        content = message.get("content", "")
        sources = message.get("sources", [])

        lines.append(f"{role}:")
        lines.append(content)

        if sources:
            lines.append("")
            lines.append("Sources:")

            for source in sources:
                lines.append(
                    f"- {format_source_for_export(source)}"
                )

        lines.append("")
        lines.append("-" * 60)
        lines.append("")

    return "\n".join(lines)


def render_history_download() -> None:
    """Render conversation controls in the sidebar."""

    with st.sidebar:
        st.subheader("💬 Conversation")

        messages = st.session_state.get("messages", [])

        if not messages:
            st.caption(
                "Download and clear options will appear after "
                "you start a conversation."
            )
            return

        history_text = build_chat_history()

        st.download_button(
            label="Download Chat History",
            data=history_text,
            file_name="medidoc_chat_history.txt",
            mime="text/plain",
            use_container_width=True,
        )

        if st.button(
            "Clear Conversation",
            use_container_width=True,
        ):
            st.session_state.messages = []
            st.rerun()
