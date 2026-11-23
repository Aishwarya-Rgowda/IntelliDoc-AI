from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    documents: Mapped[list["Document"]] = relationship(back_populates="owner", cascade="all, delete-orphan")

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    extracted_text: Mapped[str] = mapped_column(Text, default="")
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    owner: Mapped[User] = relationship(back_populates="documents")
