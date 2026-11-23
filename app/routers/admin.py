from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import ADMIN_EMAILS
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Document, User

router = APIRouter(prefix="/api/admin", tags=["Admin"])


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.email.lower() not in ADMIN_EMAILS:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access is required")
    return user


@router.get("/dashboard")
def dashboard(admin: User = Depends(require_admin), db: Session = Depends(get_db)):
    user_count = db.query(func.count(User.id)).scalar() or 0
    document_count = db.query(func.count(Document.id)).scalar() or 0
    recent = (
        db.query(Document.filename, Document.file_type, Document.uploaded_at, User.email)
        .join(User, User.id == Document.owner_id)
        .order_by(Document.uploaded_at.desc())
        .limit(10)
        .all()
    )
    return {
        "admin": admin.email,
        "total_users": user_count,
        "total_documents": document_count,
        "recent_uploads": [
            {"filename": row.filename, "file_type": row.file_type, "uploaded_at": row.uploaded_at, "owner_email": row.email}
            for row in recent
        ],
    }
