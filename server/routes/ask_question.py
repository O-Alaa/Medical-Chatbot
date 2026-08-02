import os

from dotenv import load_dotenv
from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from pinecone import Pinecone
from pydantic import Field

from logger import logger
from modules.llm import get_llm_chain
from modules.query_handlers import query_chain


# Load environment variables.
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv(
    "PINECONE_INDEX_NAME",
    "medicalindex",
)

EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMENSION = 768


# Validate required environment variables.
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY was not found in the .env file.")

if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY was not found in the .env file.")


# Initialize reusable Pinecone and embedding clients.
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pinecone_client.Index(PINECONE_INDEX_NAME)

embedding_model = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    google_api_key=GOOGLE_API_KEY,
    output_dimensionality=EMBEDDING_DIMENSION,
)


router = APIRouter()


class SimpleRetriever(BaseRetriever):
    """
    A simple LangChain retriever that returns documents already
    retrieved from Pinecone.
    """

    documents: list[Document] = Field(default_factory=list)

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager=None,
    ) -> list[Document]:
        return self.documents


def prepare_question(question: str) -> str:
    """
    Add the question-answering instruction recommended for
    Gemini Embedding 2.
    """

    return f"task: question answering | query: {question}"


@router.post("/ask/")
def ask_question(question: str = Form(...)):
    """
    Retrieve relevant PDF chunks from Pinecone and generate
    an answer using the Groq language model.
    """

    try:
        question = question.strip()

        if not question:
            return JSONResponse(
                status_code=400,
                content={"error": "The question cannot be empty."},
            )

        logger.info("User query: %s", question)

        # Format and embed the user's question.
        prepared_question = prepare_question(question)

        query_embedding = embedding_model.embed_query(
            prepared_question
        )

        logger.debug(
            "Query embedding dimension: %d",
            len(query_embedding),
        )

        # Retrieve the three most relevant chunks.
        query_result = pinecone_index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True,
        )

        matches = getattr(query_result, "matches", None)

        if matches is None:
            matches = query_result.get("matches", [])

        logger.info("Pinecone returned %d match(es)", len(matches))

        documents: list[Document] = []

        for match in matches:
            # Support both dictionary and Pinecone object responses.
            if isinstance(match, dict):
                metadata = match.get("metadata", {}) or {}
                score = match.get("score")
            else:
                metadata = getattr(match, "metadata", {}) or {}
                score = getattr(match, "score", None)

            chunk_text = metadata.get("text", "").strip()

            # Ignore Pinecone results that do not contain actual text.
            if not chunk_text:
                continue

            document_metadata = {
                **metadata,
                "score": score,
            }

            documents.append(
                Document(
                    page_content=chunk_text,
                    metadata=document_metadata,
                )
            )

        if not documents:
            logger.warning(
                "Pinecone returned no usable document text"
            )

            return JSONResponse(
                status_code=404,
                content={
                    "error": (
                        "No relevant document content was found. "
                        "Upload the PDF again and retry the question."
                    )
                },
            )

        # Pass the retrieved documents into the RAG chain.
        retriever = SimpleRetriever(documents=documents)
        chain = get_llm_chain(retriever)

        result = query_chain(
            chain=chain,
            user_input=question,
        )

        logger.info("Query processed successfully")

        return result

    except Exception as error:
        logger.exception("Error processing question")

        return JSONResponse(
            status_code=500,
            content={"error": str(error)},
        )