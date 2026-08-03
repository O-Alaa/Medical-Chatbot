import streamlit as st

from utils.api import APIError, upload_pdfs_api


def render_selected_files(uploaded_files) -> None:
    """Display the PDF files currently selected by the user."""

    if not uploaded_files:
        return

    with st.expander(
        f"Selected PDFs ({len(uploaded_files)})",
        expanded=True,
    ):
        for uploaded_file in uploaded_files:
            file_size_mb = uploaded_file.size / (1024 * 1024)

            st.caption(
                f"📄 {uploaded_file.name} — {file_size_mb:.2f} MB"
            )


def render_uploaded_documents() -> None:
    """Display PDFs uploaded during the current browser session."""

    uploaded_documents = st.session_state.get(
        "uploaded_documents",
        [],
    )

    if not uploaded_documents:
        return

    with st.expander(
        f"Uploaded this session ({len(uploaded_documents)})",
        expanded=False,
    ):
        for document_name in uploaded_documents:
            st.caption(f"✅ {document_name}")


def render_uploader() -> None:
    """Render the PDF upload controls inside the sidebar."""

    # Defensive initialization prevents AttributeError even if this
    # component is called before app.py initializes the session state.
    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = []

    with st.sidebar:
        st.title("🚑 Medical Assistant Chatbot")

        st.caption(
            "Upload trusted medical PDFs to expand the knowledge base."
        )

        st.divider()

        st.subheader("📚 Upload Documents")

        uploaded_files = st.file_uploader(
            label="Select medical PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            help=(
                "Select one or more PDF documents. They will be processed "
                "and stored in the Pinecone knowledge base."
            ),
        )

        render_selected_files(uploaded_files)

        upload_clicked = st.button(
            "Process Documents",
            type="primary",
            use_container_width=True,
            disabled=not uploaded_files,
        )

        if upload_clicked and uploaded_files:
            try:
                with st.spinner(
                    "Uploading documents and creating embeddings..."
                ):
                    result = upload_pdfs_api(uploaded_files)

                uploaded_names = [
                    uploaded_file.name
                    for uploaded_file in uploaded_files
                ]

                # Use .get() so the uploader remains safe even if the
                # session-state variable is unexpectedly missing.
                existing_documents = set(
                    st.session_state.get(
                        "uploaded_documents",
                        [],
                    )
                )

                existing_documents.update(uploaded_names)

                st.session_state.uploaded_documents = sorted(
                    existing_documents
                )

                processed_count = result.get(
                    "files_processed",
                    len(uploaded_files),
                )

                st.success(
                    f"{processed_count} PDF file(s) processed successfully."
                )

                st.toast(
                    "Medical knowledge base updated.",
                    icon="✅",
                )

            except APIError as error:
                st.error(f"Upload failed: {error}")

            except Exception as error:
                st.error(
                    "An unexpected error occurred while uploading "
                    f"the documents: {error}"
                )

        render_uploaded_documents()

        st.divider()

        st.caption(
            "Use trusted and legally shareable medical documents only."
        )
