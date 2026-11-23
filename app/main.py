from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import APP_NAME, BASE_DIR, UPLOAD_DIR, SECRET_KEY
from app.database import Base, engine
from app.routers import auth, documents, questions, summaries, duplicates, anomalies, admin

Base.metadata.create_all(bind=engine)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=APP_NAME, version="1.0.0", description="Private document library with extraction and retrieval-based Q&A.")
app.add_middleware(CORSMiddleware, allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(questions.router)
app.include_router(summaries.router)
app.include_router(duplicates.router)
app.include_router(anomalies.router)
app.include_router(admin.router)

@app.get("/api/health", tags=["System"])
def health():
    return {"status": "ok", "application": APP_NAME}

@app.get("/", include_in_schema=False)
def root():
    from fastapi.responses import FileResponse
    return FileResponse(BASE_DIR / "frontend" / "index.html")

app.mount("/static", StaticFiles(directory=BASE_DIR / "frontend"), name="static")
