import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import documents, qa

# ─── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# ─── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Document Q&A API",
    description="RAG-powered document question answering system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ─── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ───────────────────────────────────────────────────────────────────
app.include_router(documents.router)
app.include_router(qa.router)


# ─── Root ──────────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "name": "AI Document Q&A System",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /api/documents/upload",
            "list_docs": "GET /api/documents/",
            "delete_doc": "DELETE /api/documents/{doc_id}",
            "ask": "POST /api/qa/ask",
            "health": "GET /api/qa/health"
        }
    }


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
