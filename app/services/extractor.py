from io import BytesIO
from pathlib import Path
from docx import Document as DocxDocument
from pypdf import PdfReader

def extract_text(filename: str, content: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".txt":
        return content.decode("utf-8", errors="replace").strip()
    if suffix == ".pdf":
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    if suffix == ".docx":
        doc = DocxDocument(BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs).strip()
    raise ValueError("Unsupported document format")
