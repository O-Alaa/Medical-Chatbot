from typing import Annotated

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from logger import logger
from modules.load_vectorstore import load_vectorstore


router = APIRouter()


@router.post(
    "/upload_pdfs/",
    summary="Upload PDF documents",
    description=(
        "Upload one or more PDF documents, extract their text, "
        "generate embeddings, and store the vectors in Pinecone."
    ),
)
def upload_pdfs(
    files: Annotated[
        list[UploadFile],
        File(description="Select one or more PDF files"),
    ],
):
    """
    Validate and process uploaded PDF documents.

    The uploaded files are:
    1. Validated to ensure they are PDF files.
    2. Saved and processed by load_vectorstore().
    3. Split into chunks and converted into embeddings.
    4. Stored in Pinecone.
    """

    try:
        # Make sure at least one file was provided
        if not files:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "No files were provided.",
                },
            )

        # Find files that do not have a valid PDF filename
        invalid_files = [
            uploaded_file.filename
            for uploaded_file in files
            if not uploaded_file.filename
            or not uploaded_file.filename.lower().endswith(".pdf")
        ]

        # Reject the entire request if any invalid files are found
        if invalid_files:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Only PDF files are supported.",
                    "invalid_files": invalid_files,
                },
            )

        uploaded_filenames = [
            uploaded_file.filename
            for uploaded_file in files
        ]

        logger.info(
            "Received %d uploaded PDF file(s): %s",
            len(files),
            uploaded_filenames,
        )

        # Process the PDFs and store their vectors in Pinecone
        load_vectorstore(files)

        logger.info(
            "Successfully processed %d PDF file(s)",
            len(files),
        )

        return {
            "message": "Files processed and vector store updated.",
            "files_processed": len(files),
            "uploaded_files": uploaded_filenames,
        }

    except Exception as error:
        logger.exception("Error during PDF upload")

        return JSONResponse(
            status_code=500,
            content={
                "error": str(error),
            },
        )
