from pathlib import Path

from logger import logger


def query_chain(chain, user_input: str) -> dict:
    """
    Run the RAG chain and format the response and source documents.
    """

    try:
        logger.debug(
            "Running chain for input: %s",
            user_input,
        )

        # invoke() is the current LangChain execution method.
        result = chain.invoke(
            {"query": user_input}
        )

        sources = []
        seen_sources = set()

        for document in result.get(
            "source_documents",
            [],
        ):
            metadata = document.metadata

            source_path = (
                metadata.get("source_file")
                or metadata.get("source")
                or "Unknown source"
            )

            source_name = Path(str(source_path)).name

            page = metadata.get("page")

            # PyPDF page numbers begin at zero.
            if isinstance(page, int):
                page = page + 1

            source_key = (
                source_name,
                page,
            )

            # Avoid returning duplicate source entries.
            if source_key in seen_sources:
                continue

            seen_sources.add(source_key)

            sources.append(
                {
                    "file": source_name,
                    "page": page,
                    "score": metadata.get("score"),
                }
            )

        response = {
            "response": result.get("result", ""),
            "sources": sources,
        }

        logger.debug(
            "Chain response: %s",
            response,
        )

        return response

    except Exception:
        logger.exception("Error while running query chain")
        raise