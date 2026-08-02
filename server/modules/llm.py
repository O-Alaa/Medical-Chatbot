import os

from dotenv import load_dotenv
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq


# Load environment variables.
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


MEDICAL_PROMPT_TEMPLATE = """
You are MediBot, an AI-powered assistant designed to help users
understand medical documents and health-related information.

Answer the user's question using only the supplied context.

Context:
{context}

User question:
{question}

Instructions:
- Respond in a calm, factual, and respectful tone.
- Explain medical terminology using simple language when needed.
- Base the answer only on the supplied context.
- Do not invent information.
- Do not diagnose the user.
- Do not recommend medication or treatment.
- If the answer is not available in the context, respond exactly with:
  "I'm sorry, but I couldn't find relevant information in the provided documents."

Answer:
"""


def get_llm_chain(retriever):
    """
    Create a Retrieval-Augmented Generation chain using
    retrieved Pinecone documents and the Groq language model.
    """

    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY was not found in the .env file."
        )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0,
    )

    prompt = PromptTemplate(
        input_variables=["context", "question"],
        template=MEDICAL_PROMPT_TEMPLATE,
    )

    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={
            "prompt": prompt,
        },
        return_source_documents=True,
    )