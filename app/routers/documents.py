from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from app.config import ALLOWED_EXTENSIONS, MAX_UPLOAD_MB, UPLOAD_DIR
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Document, User
from app.schemas import DocumentResponse
from app.services.extractor import extract_text

router = APIRouter(prefix="/api/documents", tags=["Documents"])

def to_response(doc: Document):
    return DocumentResponse(id=doc.id, filename=doc.filename, file_type=doc.file_type, uploaded_at=doc.uploaded_at, characters=len(doc.extracted_text))

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX and TXT files are supported")
    content = await file.read((MAX_UPLOAD_MB * 1024 * 1024) + 1)
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds {MAX_UPLOAD_MB} MB limit")
    try:
        text = extract_text(file.filename or "document", content)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read document: {exc}")
    if not text:
        raise HTTPException(status_code=422, detail="No readable text found. Scanned PDFs need OCR, which is not enabled in this starter version.")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}{suffix}"
    (UPLOAD_DIR / stored_name).write_bytes(content)
    doc = Document(owner_id=user.id, filename=Path(file.filename or "document").name, stored_name=stored_name, file_type=suffix[1:], extracted_text=text)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return to_response(doc)

@router.get("", response_model=list[DocumentResponse])
def list_documents(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.owner_id == user.id).order_by(Document.uploaded_at.desc()).all()
    return [to_response(doc) for doc in docs]

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id, Document.owner_id == user.id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    path = UPLOAD_DIR / doc.stored_name
    if path.exists():
        path.unlink()
    db.delete(doc)
    db.commit()
