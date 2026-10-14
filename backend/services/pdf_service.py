import fitz  # PyMuPDF
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: Path) -> dict:
    """
    Extract text from a PDF file, page by page.
    
    Returns:
        {
            "pages": [{"page_number": 1, "text": "..."}],
            "total_pages": int,
            "full_text": str
        }
    """
    pages = []
    full_text_parts = []

    try:
        doc = fitz.open(str(file_path))
        total_pages = len(doc)

        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text("text").strip()

            if text:  # Skip blank pages
                pages.append({
                    "page_number": page_num + 1,  # 1-indexed
                    "text": text
                })
                full_text_parts.append(f"[Page {page_num + 1}]\n{text}")

        doc.close()

        logger.info(f"Extracted {total_pages} pages from {file_path.name}")

        return {
            "pages": pages,
            "total_pages": total_pages,
            "full_text": "\n\n".join(full_text_parts)
        }

    except Exception as e:
        logger.error(f"Failed to extract text from {file_path}: {e}")
        raise ValueError(f"Could not read PDF: {str(e)}")


def get_pdf_page_count(file_path: Path) -> int:
    """Quick helper to get just the page count."""
    try:
        doc = fitz.open(str(file_path))
        count = len(doc)
        doc.close()
        return count
    except Exception as e:
        raise ValueError(f"Could not open PDF: {str(e)}")
