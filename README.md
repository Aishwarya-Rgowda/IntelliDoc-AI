# IntelliDoc AI

A learning-friendly document intelligence web application built with FastAPI, SQLite, SQLAlchemy and vanilla JavaScript. Users can register, sign in, upload documents, extract text and retrieve relevant passages by asking questions.

> This is the first working foundation, not a claim that every planned AI feature is complete.

## Included now
- Registration and login with Argon2 password hashing
- Signed JWT bearer tokens with expiry
- User-scoped document access
- PDF, DOCX and TXT text extraction
- Optional OCR fallback for scanned PDFs (requires Tesseract plus `pip install -r requirements-ocr.txt`)
- Initial retrieval-service unit tests and GitHub Actions test workflow
- File extension and size checks; random storage filenames
- Keyword-based passage retrieval with source references
- Per-document extractive summaries with word-count metadata
- Exact and near-duplicate detection scoped to the signed-in user's documents
- Document-quality anomaly warnings (short, empty, unusually long or corrupted-looking extraction)
- Optional admin dashboard protected by an explicit email allowlist
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

## Optional OCR for scanned PDFs

Install the system Tesseract OCR application first, then install the Python extras:

```powershell
pip install -r requirements-ocr.txt
```

The backend tries normal PDF text extraction first and uses OCR only when no text is found. OCR language defaults to the Tesseract installation defaults.

## Run tests

```powershell
pytest -q
```

## Optional semantic search

The default mode uses lightweight keyword matching and does not download an AI model. To enable local sentence-embedding similarity, install the optional package set:

```powershell
pip install -r requirements-ai.txt
```

Then set `ENABLE_SEMANTIC_SEARCH=true` in your `.env` file and restart the server. The first semantic query downloads the `all-MiniLM-L6-v2` model and may take longer. Model inference runs locally after download. If the optional dependency or model is unavailable, retrieval falls back to keyword matching. This is semantic passage retrieval; the current answer is still extractive and does not generate new answers with an LLM.

## Grounded LLM answers (optional)

The question endpoint first retrieves relevant passages from the signed-in user's documents. To enable generated, source-grounded answers, install the optional AI dependencies and set `OPENAI_API_KEY` in your local `.env` file:

```powershell
pip install -r requirements-ai.txt
```

Set `OPENAI_MODEL=gpt-4.1-mini` (or another model available to your API account). The key stays on the backend and must never be placed in frontend JavaScript or committed to Git. Requests use `store=False`. If the key is absent or the provider is unavailable, the app safely falls back to extractive passage results. API usage may incur charges. Retrieved document text is sent to the configured provider when this feature is enabled; do not upload confidential documents unless you are permitted to share them with that provider.

## API
| Method | Endpoint | Purpose |
|---|---|---|
| POST | /api/auth/register | Create account |
| POST | /api/auth/login | Receive access token |
| GET | /api/auth/me | Current user |
| POST | /api/documents/upload | Upload/extract a document |
| GET | /api/documents | List your documents |
| DELETE | /api/documents/{id} | Delete your document |
| POST | /api/questions/ask | Retrieve relevant passages |
| POST | /api/documents/{id}/summarize | Create an extractive summary of your document |
| GET | /api/documents/duplicates | Find exact and near-duplicate documents in your library |
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
- Optional local sentence embeddings improve passage retrieval. Optional OpenAI-backed grounded answer generation is available when configured; otherwise the app returns extractive passages.
- Next: persistent vector indexing, abstractive summarization, anomaly detection, broader automated tests, database migrations and deployment hardening.

Never commit your real .env, uploaded documents, database, API keys or production secrets. Uploaded files are not served as public static files.
