import os
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from tqdm.auto import tqdm

from logger import logger


# Load environment variables.
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

PINECONE_REGION = "us-east-1"
PINECONE_INDEX_NAME = os.getenv(
    "PINECONE_INDEX_NAME",
    "medicalindex",
)

EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMENSION = 768


# modules/load_vectorstore.py -> modules -> server
SERVER_DIRECTORY = Path(__file__).resolve().parent.parent

# The PDFs will be saved inside server/uploaded_docs.
UPLOAD_DIRECTORY = SERVER_DIRECTORY / "uploaded_docs"
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


# Validate required environment variables.
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY was not found in the .env file.")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY was not found in the .env file.")


# Initialize Pinecone.
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

serverless_spec = ServerlessSpec(
    cloud="aws",
    region=PINECONE_REGION,
)


def get_existing_index_names() -> set[str]:
    """Return the names of all available Pinecone indexes."""

    index_names = set()

    for existing_index in pinecone_client.list_indexes():
        if hasattr(existing_index, "name"):
            index_names.add(existing_index.name)
        else:
            index_names.add(existing_index["name"])

    return index_names


# Create the index if it does not already exist.
if PINECONE_INDEX_NAME not in get_existing_index_names():
    logger.info(
        "Creating Pinecone index: %s",
        PINECONE_INDEX_NAME,
    )

    pinecone_client.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=EMBEDDING_DIMENSION,
        metric="dotproduct",
        spec=serverless_spec,
    )

    # Wait until Pinecone finishes creating the index.
    while True:
        index_description = pinecone_client.describe_index(
            PINECONE_INDEX_NAME
        )

        status = index_description.status

        if isinstance(status, dict):
            is_ready = status.get("ready", False)
        else:
            is_ready = getattr(status, "ready", False)

        if is_ready:
            break

        time.sleep(1)


pinecone_index = pinecone_client.Index(
    PINECONE_INDEX_NAME
)


def clean_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    """
    Convert PDF metadata into values supported by Pinecone.
    """

    cleaned_metadata = {}

    for key, value in metadata.items():
        if value is None:
            continue

        if isinstance(value, (str, int, float, bool)):
            cleaned_metadata[key] = value
        elif (
            isinstance(value, list)
            and all(isinstance(item, str) for item in value)
        ):
            cleaned_metadata[key] = value
        else:
            cleaned_metadata[key] = str(value)

    return cleaned_metadata


def prepare_document(
    content: str,
    title: str,
) -> str:
    """
    Format document text for Gemini Embedding 2 retrieval.
    """

    return f"title: {title} | text: {content}"


def load_vectorstore(uploaded_files) -> None:
    """
    Save uploaded PDFs, extract their text, split the text into
    chunks, generate embeddings, and upload them to Pinecone.
    """

    embedding_model = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=GOOGLE_API_KEY,
        output_dimensionality=EMBEDDING_DIMENSION,
    )

    saved_file_paths: list[Path] = []

    # Save uploaded PDFs locally.
    for uploaded_file in uploaded_files:
        if not uploaded_file.filename:
            continue

        # Prevent directory traversal through uploaded filenames.
        safe_filename = Path(uploaded_file.filename).name

        if not safe_filename.lower().endswith(".pdf"):
            raise ValueError(
                f"{safe_filename} is not a PDF file."
            )

        save_path = UPLOAD_DIRECTORY / safe_filename

        uploaded_file.file.seek(0)

        with open(save_path, "wb") as destination:
            destination.write(uploaded_file.file.read())

        saved_file_paths.append(save_path)

        logger.info("Saved uploaded PDF: %s", save_path)

    if not saved_file_paths:
        raise ValueError("No valid PDF files were received.")

    # Process each saved PDF.
    for file_path in saved_file_paths:
        logger.info("Loading PDF: %s", file_path.name)

        loader = PyPDFLoader(str(file_path))
        loaded_documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
        )

        chunks = text_splitter.split_documents(
            loaded_documents
        )

        # Remove chunks that contain no readable text.
        chunks = [
            chunk
            for chunk in chunks
            if chunk.page_content.strip()
        ]

        if not chunks:
            logger.warning(
                "No readable text found in %s",
                file_path.name,
            )
            continue

        logger.info(
            "Created %d chunks from %s",
            len(chunks),
            file_path.name,
        )

        embeddings: list[list[float]] = []

        # Embed one chunk at a time so every chunk receives
        # its own separate embedding.
        for chunk in tqdm(
            chunks,
            desc=f"Embedding {file_path.name}",
        ):
            prepared_text = prepare_document(
                content=chunk.page_content,
                title=file_path.name,
            )

            embedding = embedding_model.embed_query(
                prepared_text
            )

            if len(embedding) != EMBEDDING_DIMENSION:
                raise ValueError(
                    "Unexpected embedding dimension. "
                    f"Expected {EMBEDDING_DIMENSION}, "
                    f"received {len(embedding)}."
                )

            embeddings.append(embedding)

        vectors = []

        for chunk_number, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            metadata = clean_metadata(chunk.metadata)

            # Store the actual chunk text because the question
            # endpoint retrieves this value from Pinecone.
            metadata.update(
                {
                    "text": chunk.page_content,
                    "source_file": file_path.name,
                    "chunk_number": chunk_number,
                }
            )

            vector_id = (
                f"{file_path.stem}-{chunk_number}"
            )

            vectors.append(
                {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": metadata,
                }
            )

        logger.info(
            "Uploading %d vectors to Pinecone",
            len(vectors),
        )

        batch_size = 100

        with tqdm(
            total=len(vectors),
            desc=f"Uploading {file_path.name}",
        ) as progress:
            for start in range(
                0,
                len(vectors),
                batch_size,
            ):
                batch = vectors[
                    start : start + batch_size
                ]

                pinecone_index.upsert(
                    vectors=batch
                )

                progress.update(len(batch))

        logger.info(
            "Upload completed for %s",
            file_path.name,
        )