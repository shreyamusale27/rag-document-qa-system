import logging
from fastapi import APIRouter, HTTPException
from models.schemas import QuestionRequest, AnswerResponse
from services.llm_service import answer_question
from services.document_registry import get_all_documents, document_exists
from config import OPENAI_API_KEY

router = APIRouter(prefix="/api/qa", tags=["Q&A"])
logger = logging.getLogger(__name__)


@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question against uploaded documents.
    Retrieves relevant passages and generates a grounded answer.
    """
    # Validate API key is set
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key not configured. Please set OPENAI_API_KEY in your .env file."
        )

    # Validate doc IDs if provided
    if request.document_ids:
        invalid_ids = [d for d in request.document_ids if not document_exists(d)]
        if invalid_ids:
            raise HTTPException(
                status_code=404,
                detail=f"Documents not found: {', '.join(invalid_ids)}"
            )

    # Ensure at least one document is ready
    all_docs = get_all_documents()
    ready_docs = [d for d in all_docs if d.status == "ready"]

    if not ready_docs:
        raise HTTPException(
            status_code=422,
            detail="No documents are ready for querying. Please upload and wait for indexing to complete."
        )

    try:
        result = answer_question(
            question=request.question,
            document_ids=request.document_ids,
            max_sources=request.max_sources
        )
        return result

    except Exception as e:
        logger.error(f"Error answering question: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}"
        )


@router.get("/health")
async def qa_health():
    """Check if Q&A service is ready."""
    all_docs = get_all_documents()
    ready_docs = [d for d in all_docs if d.status == "ready"]
    api_configured = bool(OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here")

    return {
        "status": "ready" if (api_configured and ready_docs) else "not_ready",
        "api_configured": api_configured,
        "documents_indexed": len(ready_docs),
        "total_documents": len(all_docs)
    }
