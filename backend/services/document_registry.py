"""
Simple JSON-backed document registry.
Stores metadata about uploaded documents so we can serve
document lists without relying solely on filesystem state.
"""
import json
import logging
from pathlib import Path
from datetime import datetime
from models.schemas import DocumentInfo
from config import BASE_DIR

logger = logging.getLogger(__name__)

REGISTRY_FILE = BASE_DIR / "document_registry.json"


def _load_registry() -> dict:
    if REGISTRY_FILE.exists():
        try:
            with open(REGISTRY_FILE) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_registry(data: dict):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(data, f, indent=2, default=str)


def register_document(doc: DocumentInfo):
    """Add or update a document record."""
    registry = _load_registry()
    registry[doc.id] = doc.model_dump()
    registry[doc.id]["upload_time"] = doc.upload_time.isoformat()
    _save_registry(registry)
    logger.info(f"Registered document: {doc.id} ({doc.filename})")


def update_document_status(doc_id: str, status: str, chunk_count: int = None):
    """Update the status of a registered document."""
    registry = _load_registry()
    if doc_id in registry:
        registry[doc_id]["status"] = status
        if chunk_count is not None:
            registry[doc_id]["chunk_count"] = chunk_count
        _save_registry(registry)


def get_document(doc_id: str) -> DocumentInfo | None:
    registry = _load_registry()
    if doc_id in registry:
        data = registry[doc_id]
        data["upload_time"] = datetime.fromisoformat(data["upload_time"])
        return DocumentInfo(**data)
    return None


def get_all_documents() -> list[DocumentInfo]:
    registry = _load_registry()
    docs = []
    for data in registry.values():
        try:
            d = dict(data)
            d["upload_time"] = datetime.fromisoformat(d["upload_time"])
            docs.append(DocumentInfo(**d))
        except Exception as e:
            logger.warning(f"Skipping malformed registry entry: {e}")
    docs.sort(key=lambda d: d.upload_time, reverse=True)
    return docs


def delete_document(doc_id: str) -> bool:
    registry = _load_registry()
    if doc_id in registry:
        del registry[doc_id]
        _save_registry(registry)
        return True
    return False


def document_exists(doc_id: str) -> bool:
    return doc_id in _load_registry()
