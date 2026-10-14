import logging
import time
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import Document
from services.vector_store import search_documents
from models.schemas import SourceChunk, AnswerResponse
from config import LLM_MODEL, OPENAI_API_KEY, RETRIEVAL_K

logger = logging.getLogger(__name__)

# ─── Prompt Template ───────────────────────────────────────────────────────────
RAG_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert document analyst. Answer the user's question using ONLY the provided context from their uploaded documents.

Rules:
1. Answer based solely on the provided context — do not use outside knowledge.
2. If the answer is not in the context, say "I couldn't find relevant information in the uploaded documents."
3. Be concise, accurate, and well-structured.
4. Reference specific details from the source material when possible.
5. Do NOT make up information.

Context from documents:
{context}
"""),
    ("human", "{question}")
])


def _format_context(docs_with_scores: list[tuple[Document, float]]) -> str:
    """Format retrieved chunks into a readable context block."""
    parts = []
    for i, (doc, score) in enumerate(docs_with_scores, 1):
        meta = doc.metadata
        parts.append(
            f"[Source {i} | {meta.get('doc_name', 'Unknown')} | "
            f"Page {meta.get('page_number', '?')}]\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(parts)


def answer_question(
    question: str,
    document_ids: list[str] | None = None,
    max_sources: int = 5
) -> AnswerResponse:
    """
    Full RAG pipeline:
    1. Retrieve relevant chunks from FAISS
    2. Build context
    3. Generate answer with LLM
    4. Return structured response with source citations
    """
    start_time = time.time()

    # ── Step 1: Retrieve relevant chunks ──────────────────────────────────────
    retrieved = search_documents(
        query=question,
        doc_ids=document_ids,
        k=max_sources
    )

    if not retrieved:
        return AnswerResponse(
            question=question,
            answer="No documents have been uploaded yet, or no relevant content was found. Please upload PDF documents first.",
            sources=[],
            model_used=LLM_MODEL,
            processing_time_ms=int((time.time() - start_time) * 1000)
        )

    # ── Step 2: Build context string ─────────────────────────────────────────
    context = _format_context(retrieved)

    # ── Step 3: Call LLM ──────────────────────────────────────────────────────
    llm = ChatOpenAI(
        model=LLM_MODEL,
        openai_api_key=OPENAI_API_KEY,
        temperature=0.1,  # Low temperature for factual answers
        max_tokens=1500
    )

    chain = RAG_PROMPT | llm
    response = chain.invoke({"context": context, "question": question})
    answer_text = response.content

    # ── Step 4: Build source citations ────────────────────────────────────────
    sources = []
    for doc, score in retrieved:
        meta = doc.metadata
        # Clamp score between 0 and 1
        clamped_score = max(0.0, min(1.0, float(score)))
        sources.append(SourceChunk(
            doc_id=meta.get("doc_id", ""),
            document_name=meta.get("doc_name", "Unknown"),
            page_number=meta.get("page_number", 0),
            content=doc.page_content[:400] + ("..." if len(doc.page_content) > 400 else ""),
            relevance_score=round(clamped_score, 3)
        ))

    elapsed_ms = int((time.time() - start_time) * 1000)
    logger.info(
        f"RAG answer generated in {elapsed_ms}ms | "
        f"{len(sources)} sources | model={LLM_MODEL}"
    )

    return AnswerResponse(
        question=question,
        answer=answer_text,
        sources=sources,
        model_used=LLM_MODEL,
        processing_time_ms=elapsed_ms
    )
