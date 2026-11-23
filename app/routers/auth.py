from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import RegisterRequest, TokenResponse, UserResponse
from app.security import create_access_token, hash_password, verify_password
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    email = str(payload.email).lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(full_name=payload.full_name.strip(), email=email, hashed_password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    email = form.username.lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password", headers={"WWW-Authenticate": "Bearer"})
    token, expires_in = create_access_token(str(user.id))
    return TokenResponse(access_token=token, expires_in=expires_in)

@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return user
