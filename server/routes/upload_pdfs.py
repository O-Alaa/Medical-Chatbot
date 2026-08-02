from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from logger import logger
from modules.load_vectorstore import load_vectorstore


router = APIRouter()


@router.post("/upload_pdfs/")
def upload_pdfs(files: list[UploadFile] = File(...)):
    """
    Upload PDF documents, extract their text, generate embeddings,
    and store the resulting vectors in Pinecone.
    """

    try:
        if not files:
            return JSONResponse(
                status_code=400,
                content={"error": "No files were provided."},
            )

        # Reject files that do not have a PDF extension.
        invalid_files = [
            uploaded_file.filename
            for uploaded_file in files
            if not uploaded_file.filename
            or not uploaded_file.filename.lower().endswith(".pdf")
        ]

        if invalid_files:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Only PDF files are supported.",
                    "invalid_files": invalid_files,
                },
            )

        logger.info("Received %d uploaded PDF file(s)", len(files))

        load_vectorstore(files)

        logger.info("Documents successfully added to the vector store")

        return {
            "message": "Files processed and vector store updated.",
            "files_processed": len(files),
        }

    except Exception as error:
        logger.exception("Error during PDF upload")

        return JSONResponse(
            status_code=500,
            content={"error": str(error)},
        )