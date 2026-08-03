# 🚑 Medical Assistant Chatbot

A Retrieval-Augmented Generation (RAG) application that answers medical questions using information retrieved from a curated collection of medical PDF documents.

The project combines a **Streamlit frontend**, a **FastAPI backend**, **Google Gemini embeddings**, **Pinecone vector search**, **LangChain**, and a **Groq-hosted Llama model**.

> This application is intended for educational and portfolio purposes. It is not a diagnostic tool and does not replace professional medical care.

---

## Overview

The Medical Assistant Chatbot allows users to:

- Ask questions about medical conditions and symptoms
- Upload one or more medical PDF documents
- Convert PDF content into searchable vector embeddings
- Retrieve relevant document chunks from Pinecone
- Generate context-grounded answers with a Groq-hosted LLM
- Maintain a conversation during the current browser session
- Download the conversation as a text file

The current knowledge base contains documents covering:

- Allergies and infectious diseases
- Asthma
- Chest cold
- Diabetes
- Fever, sore throat, and congestion
- Headaches
- Hypertension in adults
- Kidney diseases
- Stroke

The architecture can support additional medical topics by processing more trusted PDF documents, subject to the limits of the configured Pinecone plan.

---

## Features

### RAG Knowledge Pipeline

- Multi-PDF upload support
- PDF text extraction with `PyPDFLoader`
- Recursive chunking with overlap
- Document embeddings using Google Gemini
- Vector storage and similarity search with Pinecone
- Context-grounded answer generation through LangChain
- Groq-hosted Llama inference

### Streamlit Interface

- Professional medical chatbot interface
- Suggested questions based on the available knowledge base
- Session-based conversation history
- Question, answer, and message counters
- PDF upload controls
- Upload progress and error feedback
- Conversation clearing
- Downloadable chat history
- Medical disclaimer

### Backend

- FastAPI REST endpoints
- Multipart PDF upload handling
- PDF validation
- Centralized exception handling
- Application logging
- CORS configuration
- Environment-based API credentials

---

## Medical Disclaimer

This project provides educational information retrieved from uploaded medical documents.

It does **not**:

- Diagnose medical conditions
- Replace a doctor or qualified healthcare professional
- Prescribe medication
- Create treatment plans
- Provide emergency medical assistance

Always consult a qualified healthcare professional for medical concerns. In an emergency, contact the appropriate local emergency service immediately.

---

## System Architecture

```text
User
  |
  v
Streamlit Frontend
  |
  | HTTP requests
  v
FastAPI Backend
  |
  +--> PDF Loader
  |
  +--> Recursive Text Splitter
  |
  +--> Gemini Embeddings
  |
  +--> Pinecone Vector Database
  |
  +--> Relevant Document Retrieval
  |
  +--> LangChain RetrievalQA
  |
  +--> Groq-hosted Llama Model
  |
  v
Document-grounded response
```

---

## RAG Workflow

### 1. Document Upload

The user uploads one or more PDF documents through the Streamlit interface or the FastAPI endpoint.

### 2. Text Extraction

The backend reads each PDF with:

```python
PyPDFLoader
```

### 3. Text Chunking

Extracted pages are divided into overlapping chunks using:

```python
RecursiveCharacterTextSplitter
```

The current configuration uses:

```text
Chunk size: 500 characters
Chunk overlap: 50 characters
```

### 4. Embedding Generation

Each chunk is converted into a 768-dimensional vector using:

```text
gemini-embedding-2
```

Document chunks use the retrieval-document embedding task.

### 5. Pinecone Storage

Each vector is stored in Pinecone together with metadata such as:

- Original chunk text
- Source filename
- Source path
- Page number

### 6. Query Retrieval

When the user asks a question:

1. The question is embedded
2. Pinecone retrieves the most relevant chunks
3. The chunks are converted into LangChain documents
4. The documents are passed to the LLM as context

### 7. Answer Generation

The configured Groq model generates an answer from the retrieved context.

Current model:

```text
llama-3.3-70b-versatile
```

---

## Project Structure

```text
Medical Chatbot/
├── .gitignore
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
    ├── .env
    ├── logger.py
    ├── main.py
    ├── requirements.txt
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
```

The `.env` file and uploaded PDFs should not be committed to GitHub.

---

## Main Technologies

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Frontend application |
| FastAPI | Backend API |
| Uvicorn | ASGI application server |
| LangChain | RAG orchestration |
| LangChain Classic | RetrievalQA chain |
| Groq | LLM inference |
| Google Gemini Embeddings | Document and query embeddings |
| Pinecone | Vector database and semantic retrieval |
| PyPDF | PDF text extraction |
| Pydantic | Validation and retriever models |
| Requests | Frontend-to-backend communication |
| Python Logging | Application logging |
| Render | Deployed FastAPI backend |

---

## API Endpoints

### Upload PDFs

```http
POST /upload_pdfs/
```

Request format:

```text
multipart/form-data
```

Form field:

```text
files
```

The endpoint accepts multiple PDF files using the same field name.

Example response:

```json
{
  "message": "Files processed and vector store updated.",
  "files_processed": 1
}
```

### Ask a Question

```http
POST /ask/
```

Request format:

```text
multipart/form-data
```

Form field:

```text
question
```

Example question:

```text
What are the common symptoms and causes of headaches?
```

Example response:

```json
{
  "response": "Headaches can have several symptoms and possible triggers..."
}
```

The backend may also return source metadata. The current Streamlit interface intentionally displays only the generated answer.

---

## Deployed Backend

The FastAPI backend is deployed on Render:

```text
https://medical-chatbot-ndeq.onrender.com
```

Swagger documentation:

```text
https://medical-chatbot-ndeq.onrender.com/docs
```

The free Render instance may spin down after inactivity, so the first request can take longer while the service starts.

---

## Environment Variables

Create:

```text
server/.env
```

Add:

```env
GOOGLE_API_KEY=your_google_api_key
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_INDEX_NAME=medicalindex
GROQ_API_KEY=your_groq_api_key
```

Never commit real API keys.

The Streamlit frontend supports an optional environment variable:

```env
MEDICAL_API_URL=http://127.0.0.1:8000
```

When it is not set, the client uses the deployed Render API configured in `client/config.py`.

---

## Recommended `.gitignore`

```gitignore
# Secrets
.env
server/.env
.streamlit/secrets.toml

# Virtual environments
.venv/
venv/

# Python
__pycache__/
*.pyc
*.pyo

# Uploaded medical documents
server/uploaded_docs/

# Operating-system files
.DS_Store
Thumbs.db
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/O-Alaa/Medical-Chatbot.git
cd Medical-Chatbot
```

### 2. Create a Virtual Environment

Using `uv`:

```bash
uv venv
```

Activate it on Windows PowerShell:

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

## Running Locally

### Option A: Use the Deployed Backend

The frontend already uses the Render API by default.

Run:

```powershell
python -m streamlit run client/app.py
```

Then open:

```text
http://localhost:8501
```

### Option B: Run Both Backend and Frontend Locally

#### Terminal 1 — FastAPI

```powershell
cd server
uvicorn main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

#### Terminal 2 — Streamlit

From the project root:

```powershell
$env:MEDICAL_API_URL = "http://127.0.0.1:8000"
python -m streamlit run client/app.py
```

---

## Testing with Postman

### Upload Documents

```text
Method: POST
URL: https://medical-chatbot-ndeq.onrender.com/upload_pdfs/
Body: form-data
Key: files
Type: File
```

For multiple documents, add several rows using the same `files` key.

### Ask a Question

```text
Method: POST
URL: https://medical-chatbot-ndeq.onrender.com/ask/
Body: form-data
Key: question
Type: Text
```

---

## Suggested Questions

The interface currently includes suggestions such as:

```text
What are the common symptoms and causes of headaches?
```

```text
What are the warning signs of a stroke?
```

```text
What is hypertension and what are its risk factors?
```

```text
What are the common symptoms of asthma?
```

```text
What is diabetes and what symptoms can it cause?
```

```text
What are the symptoms of a chest cold?
```

```text
What information is available about kidney disease?
```

```text
What symptoms can occur with allergies or infectious diseases?
```

---

## Current Limitations

- Pinecone free-tier capacity limits the number of indexed document chunks
- No user authentication or separate user knowledge bases
- No document listing or deletion API
- No duplicate-document detection
- Uploaded PDFs are stored on the backend filesystem before processing
- No reranking stage after Pinecone retrieval
- No relevance-score threshold
- Follow-up questions do not include true conversational memory in backend retrieval
- Source filenames are not currently displayed in the Streamlit interface
- No medical-emergency classifier
- No automated RAG evaluation pipeline
- Render free-tier cold starts can increase response time
- The configured 70B model prioritizes answer quality over minimum latency

---

## Planned Improvements

- Add document management endpoints
- Add duplicate-document detection
- Add document categories and metadata filters
- Add source filenames and page citations
- Add retrieval relevance thresholds
- Add a reranking model
- Add conversational memory for follow-up questions
- Add medical-safety guardrails
- Add emergency-query detection
- Add user authentication
- Add per-user document collections
- Add automated RAG evaluation
- Add unit and integration tests
- Add Docker support
- Add production monitoring
- Improve deployment scalability

---

## Development Notes

Frontend API communication:

```text
client/utils/api.py
```

Frontend API configuration:

```text
client/config.py
```

FastAPI entry point:

```text
server/main.py
```

Document processing and Pinecone indexing:

```text
server/modules/load_vectorstore.py
```

Prompt and LLM configuration:

```text
server/modules/llm.py
```

Question processing:

```text
server/modules/query_handlers.py
```

API routes:

```text
server/routes/upload_pdfs.py
server/routes/ask_question.py
```

---

## Security Notes

- Do not commit `.env` files
- Do not expose API keys in frontend code
- Validate uploaded file types
- Apply upload-size limits in production
- Use trusted and legally shareable medical documents
- Add authentication before allowing public uploads
- Consider malware scanning for production file uploads

---

## License

This project is licensed under the MIT License.

You may use, modify, and distribute the source code in accordance with the license. Third-party services, models, libraries, and uploaded medical documents remain subject to their own terms and licenses.

---

## Author

**Omar Eissa**

AI Engineer portfolio project.
