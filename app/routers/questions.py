from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Document, User
from app.schemas import AnswerResponse, QuestionRequest
from app.services.retrieval import answer_question

router = APIRouter(prefix="/api/questions", tags=["Question answering"])

@router.post("/ask", response_model=AnswerResponse)
def ask(payload: QuestionRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = db.query(Document).filter(Document.owner_id == user.id)
    if payload.document_id is not None:
        query = query.filter(Document.id == payload.document_id)
    docs = query.all()
    if not docs:
        raise HTTPException(status_code=404, detail="Upload a document before asking questions")
    answer, sources = answer_question(payload.question, docs)
    return AnswerResponse(answer=answer, sources=sources)
