# IntelliDoc AI

A learning-friendly document intelligence web application built with FastAPI, SQLite, SQLAlchemy and vanilla JavaScript. Users can register, sign in, upload documents, extract text and retrieve relevant passages by asking questions.

> This is the first working foundation, not a claim that every planned AI feature is complete.

## Included now
- Registration and login with Argon2 password hashing
- Signed JWT bearer tokens with expiry
- User-scoped document access
- PDF, DOCX and TXT text extraction\n- Optional OCR fallback for scanned PDFs (requires Tesseract plus `pip install -r requirements-ocr.txt`)\n- Initial retrieval-service unit tests and GitHub Actions test workflow
- File extension and size checks; random storage filenames
- Keyword-based passage retrieval with source references
- Responsive browser interface and interactive API docs

## Run locally
Python 3.10+ recommended.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

Edit `.env` and replace SECRET_KEY with a long random value, then run:

```powershell
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000. API documentation: http://127.0.0.1:8000/docs.

## Optional OCR for scanned PDFs\n\nInstall the system Tesseract OCR application first, then install the Python extras:\n\n```powershell\npip install -r requirements-ocr.txt\n```\n\nThe backend tries normal PDF text extraction first and uses OCR only when no text is found. OCR language defaults to the Tesseract installation defaults.\n\n## Run tests\n\n```powershell\npytest -q\n```\n\n## API
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/register | Create account |
| POST | /api/auth/login | Receive access token |
| GET | /api/auth/me | Current user |
| POST | /api/documents/upload | Upload/extract a document |
| GET | /api/documents | List your documents |
| DELETE | /api/documents/{id} | Delete your document |
| POST | /api/questions/ask | Retrieve relevant passages |
| GET | /api/health | Health check |

Protected endpoints require `Authorization: Bearer <token>`.

## Authentication design
1. Registration hashes the password using Argon2 before saving it.
2. Login verifies the submitted password against the stored hash.
3. Successful login returns a signed JWT containing the user ID and expiry.
4. The frontend sends the token in the Authorization header.
5. The API validates the token and scopes document queries to the authenticated user's ID.

The educational prototype stores the access token in localStorage. A production system should prefer secure HttpOnly/SameSite cookies, HTTPS, refresh-token rotation, rate limiting, CSRF protection where applicable, and managed secrets.

## Current limitations / roadmap
- Scanned PDF OCR is available as an optional local feature. Install the packages in `requirements-ocr.txt` and the Tesseract application for your operating system; OCR is not included in the default install.
- Q&A currently retrieves relevant passages; it does not yet use embeddings, an LLM or a full RAG pipeline.
- Next: OCR, semantic embeddings/vector search, grounded RAG, summarization, duplicate/anomaly detection, automated tests, database migrations and deployment hardening.

Never commit your real .env, uploaded documents, database, API keys or production secrets. Uploaded files are not served as public static files.
