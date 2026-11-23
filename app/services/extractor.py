from io import BytesIO
from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


def _extract_pdf_text(content: bytes) -> str:
    reader = PdfReader(BytesIO(content))
    return "\n".join(page.extract_text() or "" for page in reader.pages).strip()


def _extract_scanned_pdf_text(content: bytes) -> str:
    """OCR fallback for image-only PDFs. Requires optional OCR packages and Tesseract."""
    try:
        import fitz
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "This PDF appears to be scanned. Install optional OCR dependencies "
            "from requirements-ocr.txt and install the Tesseract OCR application."
        ) from exc

    pages_text = []
    with fitz.open(stream=content, filetype="pdf") as pdf:
        for page in pdf:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.open(BytesIO(pixmap.tobytes("png")))
            pages_text.append(pytesseract.image_to_string(image))
    return "\n".join(pages_text).strip()


def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".txt":
        return content.decode("utf-8", errors="replace").strip()
    if suffix == ".pdf":
        text = _extract_pdf_text(content)
        return text if text else _extract_scanned_pdf_text(content)
    if suffix == ".docx":
        doc = DocxDocument(BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs).strip()
    raise ValueError("Unsupported document format")
