# 🧠 DocMind AI — Document Q&A System (RAG)

An AI-powered Retrieval-Augmented Generation (RAG) application. Upload PDFs, ask questions in plain English, and get precise answers grounded in your documents — with page-level source citations.

---

## ✨ Features

- 📤 **PDF Upload** — Drag-and-drop or click to upload (up to 50MB)
- ✂️ **Smart Chunking** — RecursiveCharacterTextSplitter with overlap
- 🧬 **Semantic Embeddings** — OpenAI `text-embedding-3-small`
- 🗄️ **FAISS Vector Store** — Per-document indexes, persisted to disk
- 🤖 **LLM Generation** — GPT-4o-mini with grounded RAG prompt
- 📌 **Source Citations** — Page-level citations with relevance scores
- 💬 **Chat Interface** — React frontend with multi-document Q&A
- ⚡ **Async Indexing** — Upload is instant; indexing happens in background

---

## 🗂️ Project Structure

```
rag-qa-system/
├── backend/              # FastAPI Python server
│   ├── main.py           # App entrypoint
│   ├── config.py         # Environment variables
│   ├── requirements.txt
│   ├── models/
│   │   └── schemas.py    # Pydantic models
│   ├── services/
│   │   ├── pdf_service.py          # PyMuPDF extraction
│   │   ├── embedding_service.py    # LangChain chunking + embeddings
│   │   ├── vector_store.py         # FAISS index management
│   │   ├── llm_service.py          # RAG pipeline
│   │   └── document_registry.py    # JSON metadata store
│   └── routers/
│       ├── documents.py  # Upload / list / delete
│       └── qa.py         # Ask questions
│
└── frontend/             # React + Vite frontend
    └── src/
        ├── App.jsx
        ├── components/
        │   ├── Sidebar.jsx       # Document panel
        │   ├── ChatWindow.jsx    # Message history
        │   ├── MessageBubble.jsx # User/AI messages
        │   ├── SourceCard.jsx    # Citation cards
        │   └── UploadModal.jsx   # PDF upload modal
        └── services/
            └── api.js            # Axios API client
```

---

## ⚙️ Setup

### 1. Backend

```bash
cd backend
pip install -r requirements.txt

# Create .env from template
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

python main.py
# → http://localhost:8000
# → Swagger docs: http://localhost:8000/docs
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## 🔑 Environment Variables (backend/.env)

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | **required** | Your OpenAI API key |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `LLM_MODEL` | `gpt-4o-mini` | Answer generation model |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `RETRIEVAL_K` | `5` | Number of chunks to retrieve |

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/documents/upload` | Upload a PDF |
| `GET` | `/api/documents/` | List all documents |
| `GET` | `/api/documents/{id}` | Get document info |
| `DELETE` | `/api/documents/{id}` | Delete document + index |
| `POST` | `/api/qa/ask` | Ask a question |
| `GET` | `/api/qa/health` | API health check |

### Ask a question (POST /api/qa/ask)

```json
{
  "question": "What are the key findings?",
  "document_ids": ["abc123", "def456"],  // null = search all 
  "max_sources": 5
}
```

---

## 🏗️ RAG Architecture

```
User Question
     │
     ▼
Embedding Model ──► Query Vector
     │
     ▼
FAISS Similarity Search ──► Top-K Relevant Chunks (with page metadata)
     │
     ▼
Context Assembly ──► [Page 3] text... [Page 7] text...
     │
     ▼
GPT-4o-mini ──► Grounded Answer
     │
     ▼
Response with Source Citations (doc, page, relevance %)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| PDF | PyMuPDF (fitz) |
| Chunking | LangChain RecursiveCharacterTextSplitter |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | FAISS (local, persisted) |
| LLM | OpenAI GPT-4o-mini via LangChain LCEL |
| Frontend | React 18, Vite, Axios |
| Styling | Vanilla CSS (dark glassmorphic) |
