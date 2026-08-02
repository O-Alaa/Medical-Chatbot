# Medical Chatbot

A document-based medical question-answering application built with **FastAPI**, **Streamlit**, **LangChain**, **Google Gemini Embeddings**, **Pinecone**, and **Groq**.

The current version allows users to upload medical PDF documents, convert their contents into vector embeddings, store them in Pinecone, and ask questions based on the uploaded material.

> The current demo includes a diabetes PDF, but the architecture supports additional diseases, medical conditions, guidelines, and healthcare documents by uploading more PDFs.

---

## Features

- Upload one or more medical PDF files
- Extract and split PDF text into smaller chunks
- Generate embeddings using Google Gemini
- Store and retrieve document vectors using Pinecone
- Ask medical questions through a FastAPI endpoint
- Generate context-aware answers using Groq-hosted Llama models
- Return source metadata with generated answers
- Streamlit-based frontend
- Logging and centralized exception handling
- Conversation-history export support

---

## Important Medical Disclaimer

This project is intended for educational and informational purposes only.

It does not:

- Diagnose medical conditions
- Replace a doctor or qualified healthcare professional
- Prescribe medication
- Recommend treatment plans
- Provide emergency medical assistance

The assistant should answer only from the uploaded documents. Users should always consult a qualified medical professional for medical concerns.

---

## System Architecture

```text
User
  |
  v
Streamlit Frontend
  |
  | HTTP Requests
  v
FastAPI Backend
  |
  +--> PDF Loader
  |
  +--> Text Splitter
  |
  +--> Gemini Embeddings
  |
  +--> Pinecone Vector Database
  |
  +--> LangChain RetrievalQA
  |
  +--> Groq LLM
  |
  v
Document-grounded answer
```

---

## Project Structure

```text
Medical Chatbot/
├── main.py
├── pyproject.toml
├── README.md
├── client/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── components/
│   │   ├── chatUI.py
│   │   ├── history_download.py
│   │   └── upload.py
│   └── utils/
│       └── api.py
└── server/
    ├── main.py
    ├── logger.py
    ├── requirements.txt
    ├── test.py
    ├── .env
    ├── middlewares/
    │   └── exception_handlers.py
    ├── modules/
    │   ├── llm.py
    │   ├── load_vectorstore.py
    │   ├── pdf_handlers.py
    │   └── query_handlers.py
    ├── routes/
    │   ├── ask_question.py
    │   └── upload_pdfs.py
    └── uploaded_docs/
        └── DIABETES.pdf
```

---

## Main Technologies

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | Backend API |
| Uvicorn | ASGI server |
| Streamlit | Frontend interface |
| LangChain | RAG orchestration |
| Groq | LLM inference |
| Google Gemini Embeddings | Document and query embeddings |
| Pinecone | Vector database |
| PyPDF | PDF extraction |
| Pydantic | Data validation |
| Requests | Frontend-to-backend communication |
| Loguru / Python Logging | Application logging |

---

## How the RAG Pipeline Works

### 1. PDF Upload

The user uploads one or more PDFs through the frontend or the FastAPI upload endpoint.

### 2. PDF Processing

The backend:

1. Saves the uploaded files locally
2. Extracts text using `PyPDFLoader`
3. Splits the text into overlapping chunks using `RecursiveCharacterTextSplitter`

### 3. Embedding

Each chunk is converted into a numerical vector using:

```python
GoogleGenerativeAIEmbeddings
```

The current embedding model is:

```text
gemini-embedding-2
```

### 4. Vector Storage

The vectors are stored in Pinecone with metadata such as:

- Original chunk text
- PDF filename
- Source path
- Page number

### 5. Retrieval

When the user asks a question:

1. The question is embedded
2. Pinecone searches for the most relevant chunks
3. The retrieved chunks are passed to the language model

### 6. Answer Generation

Groq runs the configured Llama model and generates an answer based only on the retrieved context.

---

## API Endpoints

### Upload PDFs

```http
POST /upload_pdfs/
```

Form-data field:

```text
files
```

Example response:

```json
{
  "messages": "Files processed and vectorstore updated"
}
```

### Ask a Question

```http
POST /ask/
```

Form-data field:

```text
question
```

Example request:

```text
What is diabetes?
```

Example response:

```json
{
  "response": "Diabetes is a chronic condition...",
  "sources": [
    "DIABETES.pdf"
  ]
}
```

---

## Environment Variables

Create a `.env` file inside the `server` directory:

```env
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=medical-index
GROQ_API_KEY=your_groq_api_key
```

Never commit the `.env` file to GitHub.

Add this to `.gitignore`:

```gitignore
.env
__pycache__/
*.pyc
.venv/
venv/
uploaded_docs/
```

---

## Installation

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd "Medical Chatbot"
```

### 2. Create a Virtual Environment

Using `uv`:

```bash
uv venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install Backend Dependencies

```bash
uv pip install -r server/requirements.txt
```

### 4. Install Frontend Dependencies

```bash
uv pip install -r client/requirements.txt
```

---

## Running the Application

### Start the FastAPI Backend

Open a terminal:

```powershell
cd server
uvicorn main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

### Start the Streamlit Frontend

Open a second terminal from the project root:

```powershell
streamlit run client/app.py
```

---

## Testing with Postman

### Upload PDFs

- Method: `POST`
- URL:

```text
http://127.0.0.1:8000/upload_pdfs/
```

- Body: `form-data`
- Key: `files`
- Type: `File`

### Ask a Question

- Method: `POST`
- URL:

```text
http://127.0.0.1:8000/ask/
```

- Body: `form-data`
- Key: `question`
- Type: `Text`

---

## Current Limitations

- The current demo knowledge base mainly contains diabetes-related content
- No authentication or user accounts
- No document deletion endpoint
- No duplicate-document detection
- Limited metadata filtering
- No reranking step
- No conversation memory across sessions
- No medical emergency detection
- No automated evaluation pipeline

---

## Planned Improvements

- Add PDFs for multiple diseases and medical specialties
- Add document listing and deletion
- Add duplicate-upload prevention
- Add source filenames and page citations
- Add category-based filtering
- Add relevance-score thresholds
- Improve the Streamlit design
- Add chat history and session management
- Add medical-safety guardrails
- Add emergency-query detection
- Add automated RAG evaluation
- Add Docker deployment
- Add cloud deployment
- Add user authentication

---

## Example Medical Categories

The knowledge base can be expanded with trusted PDFs covering:

- Diabetes
- Cardiology
- Hypertension
- Asthma
- Neurology
- Oncology
- Kidney disease
- Mental health
- Nutrition
- First aid
- Medication information
- Public-health guidelines

Only use trusted and legally shareable medical documents.

---

## Example Questions

```text
What is diabetes?
```

```text
What are the common symptoms mentioned in the document?
```

```text
What are the risk factors?
```

```text
How is the condition described in the uploaded PDF?
```

```text
What complications are mentioned?
```

---

## Development Notes

The frontend sends requests to FastAPI through:

```text
client/utils/api.py
```

The backend routes are registered in:

```text
server/main.py
```

The main RAG components are:

```text
server/modules/load_vectorstore.py
server/modules/llm.py
server/modules/query_handlers.py
```

---

## License

This project is licensed under the MIT License. You are free to use, modify, and distribute it with proper attribution.

- Uploaded medical documents
- Pinecone
- Google Gemini
- Groq
- LangChain
