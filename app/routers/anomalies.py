from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Document, User
from app.services.anomalies import inspect_documents

router = APIRouter(prefix="/api/documents", tags=["Document quality"])


@router.get("/anomalies")
def document_anomalies(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return document-quality warnings for the current user's library only."""
    documents = (
        db.query(Document)
        .filter(Document.owner_id == user.id)
        .order_by(Document.id.asc())
        .all()
    )
    findings = inspect_documents(documents)
    return {"documents_scanned": len(documents), "documents_with_warnings": len(findings), "findings": findings}
