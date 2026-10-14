import logging
import json
import shutil
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from services.embedding_service import get_embeddings
from config import FAISS_INDEX_DIR

logger = logging.getLogger(__name__)


def _index_path(doc_id: str) -> Path:
    return FAISS_INDEX_DIR / doc_id


def add_document_to_index(doc_id: str, chunks: list[Document]) -> int:
    """
    Create or overwrite a FAISS index for the given document.
    
    Returns:
        Number of chunks indexed
    """
    if not chunks:
        raise ValueError("No chunks to index")

    embeddings = get_embeddings()
    index_dir = _index_path(doc_id)

    # Remove old index if exists
    if index_dir.exists():
        shutil.rmtree(index_dir)

    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(str(index_dir))

    logger.info(f"Indexed {len(chunks)} chunks for doc '{doc_id}' → {index_dir}")
    return len(chunks)


def search_documents(
    query: str,
    doc_ids: list[str] | None = None,
    k: int = 5
) -> list[tuple[Document, float]]:
    """
    Similarity search across one or more FAISS indexes.
    
    Args:
        query: The user's question
        doc_ids: List of doc IDs to search, or None for all indexed docs
        k: Number of results per document index
    
    Returns:
        List of (Document, score) sorted by relevance (descending)
    """
    embeddings = get_embeddings()

    # Determine which indexes to search
    if doc_ids:
        index_dirs = [_index_path(d) for d in doc_ids if _index_path(d).exists()]
    else:
        index_dirs = [p for p in FAISS_INDEX_DIR.iterdir() if p.is_dir()]

    if not index_dirs:
        return []

    all_results: list[tuple[Document, float]] = []

    for index_dir in index_dirs:
        try:
            vectorstore = FAISS.load_local(
                str(index_dir),
                embeddings,
                allow_dangerous_deserialization=True
            )
            results = vectorstore.similarity_search_with_relevance_scores(query, k=k)
            all_results.extend(results)
        except Exception as e:
            logger.error(f"Error searching index at {index_dir}: {e}")

    # Sort by score descending, take top k overall
    all_results.sort(key=lambda x: x[1], reverse=True)
    return all_results[:k]


def delete_document_index(doc_id: str) -> bool:
    """Remove FAISS index for a document."""
    index_dir = _index_path(doc_id)
    if index_dir.exists():
        shutil.rmtree(index_dir)
        logger.info(f"Deleted FAISS index for doc '{doc_id}'")
        return True
    return False


def document_is_indexed(doc_id: str) -> bool:
    """Check if a FAISS index exists for this document."""
    return _index_path(doc_id).exists()
