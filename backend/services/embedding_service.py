import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from config import CHUNK_SIZE, CHUNK_OVERLAP, EMBEDDING_MODEL, OPENAI_API_KEY

logger = logging.getLogger(__name__)

# Singleton embeddings instance
_embeddings = None


def get_embeddings() -> OpenAIEmbeddings:
    """Return a cached OpenAI embeddings instance."""
    global _embeddings
    if _embeddings is None:
        _embeddings = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            openai_api_key=OPENAI_API_KEY
        )
    return _embeddings


def chunk_pages(pages: list[dict], doc_id: str, doc_name: str) -> list[Document]:
    """
    Split extracted pages into overlapping chunks.
    Each chunk carries metadata: doc_id, doc_name, page_number, chunk_index.
    
    Args:
        pages: list of {"page_number": int, "text": str}
        doc_id: unique document identifier
        doc_name: human-readable filename
    
    Returns:
        list of LangChain Document objects with metadata
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    all_chunks: list[Document] = []
    chunk_index = 0

    for page in pages:
        page_num = page["page_number"]
        text = page["text"]

        if not text.strip():
            continue

        # Split this page's text
        page_chunks = splitter.split_text(text)

        for chunk_text in page_chunks:
            chunk_text = chunk_text.strip()
            if len(chunk_text) < 20:  # Skip tiny fragments
                continue

            all_chunks.append(Document(
                page_content=chunk_text,
                metadata={
                    "doc_id": doc_id,
                    "doc_name": doc_name,
                    "page_number": page_num,
                    "chunk_index": chunk_index,
                }
            ))
            chunk_index += 1

    logger.info(
        f"Chunked doc '{doc_name}' into {len(all_chunks)} chunks "
        f"(size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})"
    )

    return all_chunks
