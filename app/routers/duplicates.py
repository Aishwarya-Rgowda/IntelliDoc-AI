from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Document, User
from app.services.duplicates import find_duplicates

router = APIRouter(prefix="/api/documents", tags=["Duplicate detection"])


@router.get("/duplicates")
def list_duplicate_documents(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Compare only documents belonging to the authenticated user."""
    documents = (
        db.query(Document)
        .filter(Document.owner_id == user.id)
        .order_by(Document.id.asc())
        .all()
    )
    return {"count": len(documents), "duplicates": find_duplicates(documents)}
