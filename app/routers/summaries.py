from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Document, User
from app.schemas import SummaryResponse
from app.services.summarizer import summarize_text

router = APIRouter(prefix="/api/documents", tags=["Document summaries"])


@router.post("/{document_id}/summarize", response_model=SummaryResponse)
def summarize_document(
    document_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.owner_id == user.id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")

    summary, original_words, summary_words = summarize_text(document.extracted_text)
    if not summary:
        raise HTTPException(status_code=422, detail="No readable text is available to summarize")

    return SummaryResponse(
        document_id=document.id,
        filename=document.filename,
        summary=summary,
        original_word_count=original_words,
        summary_word_count=summary_words,
        method="extractive",
    )
