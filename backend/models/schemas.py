from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ─── Document Schemas ──────────────────────────────────────────────────────────

class DocumentInfo(BaseModel):
    id: str
    filename: str
    original_name: str
    page_count: int
    chunk_count: int
    upload_time: datetime
    status: str  # "indexing" | "ready" | "error"
    file_size_kb: float


class DocumentListResponse(BaseModel):
    documents: list[DocumentInfo]
    total: int


class DeleteResponse(BaseModel):
    message: str
    doc_id: str


# ─── Q&A Schemas ───────────────────────────────────────────────────────────────

class SourceChunk(BaseModel):
    doc_id: str
    document_name: str
    page_number: int
    content: str
    relevance_score: float = Field(ge=0.0, le=1.0)


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    document_ids: Optional[list[str]] = None  # None = search all docs
    max_sources: int = Field(default=5, ge=1, le=10)


class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceChunk]
    model_used: str
    processing_time_ms: int


# ─── Upload Status ─────────────────────────────────────────────────────────────

class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    message: str
    status: str
