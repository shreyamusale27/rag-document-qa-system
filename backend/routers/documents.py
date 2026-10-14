import uuid
import logging
import aiofiles
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from models.schemas import DocumentInfo, DocumentListResponse, DeleteResponse, UploadResponse
from services.pdf_service import extract_text_from_pdf, get_pdf_page_count
from services.embedding_service import chunk_pages
from services.vector_store import add_document_to_index, delete_document_index
from services.document_registry import (
    register_document, update_document_status,
    get_all_documents, delete_document, document_exists
)
from config import UPLOAD_DIR

router = APIRouter(prefix="/api/documents", tags=["Documents"])
logger = logging.getLogger(__name__)

MAX_FILE_SIZE_MB = 50


async def _process_document_background(doc_id: str, file_path: Path, doc_name: str):
    """Background task: extract text → chunk → embed → index."""
    try:
        logger.info(f"[BG] Processing document {doc_id}: {doc_name}")

        # Extract text from PDF
        extracted = extract_text_from_pdf(file_path)

        if not extracted["pages"]:
            update_document_status(doc_id, "error")
            logger.warning(f"[BG] No text extracted from {doc_name}")
            return

        # Chunk into LangChain Documents
        chunks = chunk_pages(extracted["pages"], doc_id, doc_name)

        # Index into FAISS
        chunk_count = add_document_to_index(doc_id, chunks)

        # Update registry
        update_document_status(doc_id, "ready", chunk_count)

        logger.info(f"[BG] ✓ Document '{doc_name}' indexed with {chunk_count} chunks")

    except Exception as e:
        logger.error(f"[BG] Failed to process document {doc_id}: {e}")
        update_document_status(doc_id, "error")


@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload a PDF document. Indexing happens asynchronously."""

    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Read file content
    content = await file.read()

    # Check file size
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f}MB). Maximum allowed: {MAX_FILE_SIZE_MB}MB."
        )

    # Generate unique ID and save file
    doc_id = str(uuid.uuid4())[:8]
    safe_name = "".join(c if c.isalnum() or c in "._- " else "_" for c in file.filename)
    file_path = UPLOAD_DIR / f"{doc_id}_{safe_name}"

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    # Get page count quickly (without full extraction)
    try:
        page_count = get_pdf_page_count(file_path)
    except Exception:
        page_count = 0

    # Register document with "indexing" status
    doc_info = DocumentInfo(
        id=doc_id,
        filename=f"{doc_id}_{safe_name}",
        original_name=file.filename,
        page_count=page_count,
        chunk_count=0,
        upload_time=datetime.now(),
        status="indexing",
        file_size_kb=round(len(content) / 1024, 1)
    )
    register_document(doc_info)

    # Queue background processing
    background_tasks.add_task(
        _process_document_background, doc_id, file_path, file.filename
    )

    logger.info(f"Uploaded '{file.filename}' ({size_mb:.2f}MB) → doc_id={doc_id}")

    return UploadResponse(
        doc_id=doc_id,
        filename=file.filename,
        message="Document uploaded successfully. Indexing in progress...",
        status="indexing"
    )


@router.get("/", response_model=DocumentListResponse)
async def list_documents():
    """Get all uploaded documents with their status."""
    docs = get_all_documents()
    return DocumentListResponse(documents=docs, total=len(docs))


@router.get("/{doc_id}", response_model=DocumentInfo)
async def get_document_info(doc_id: str):
    """Get info for a specific document."""
    from services.document_registry import get_document
    doc = get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")
    return doc


@router.delete("/{doc_id}", response_model=DeleteResponse)
async def delete_document_endpoint(doc_id: str):
    """Delete a document and its vector index."""
    if not document_exists(doc_id):
        raise HTTPException(status_code=404, detail=f"Document '{doc_id}' not found.")

    # Remove FAISS index
    delete_document_index(doc_id)

    # Remove from registry
    delete_document(doc_id)

    # Remove uploaded file
    for file_path in UPLOAD_DIR.glob(f"{doc_id}_*"):
        file_path.unlink(missing_ok=True)

    logger.info(f"Deleted document {doc_id}")

    return DeleteResponse(message="Document deleted successfully.", doc_id=doc_id)
