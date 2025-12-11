# Basic RAG Pipeline (LangChain + OpenAI + ChromaDB)

Minimal Retrieval-Augmented Generation stack: FastAPI backend with LangChain + ChromaDB + OpenAI, plus a Next.js frontend scaffold you can wire up to the API.

## Project structure

```
backend/    # FastAPI + LangChain + ChromaDB API (Poetry)
frontend/   # Next.js app scaffold (Bun)
```

## Backend quickstart

1. Install (Python 3.10+):
   - `cd backend`
   - `poetry install`
2. Configure environment:
   - `cp env.example .env`
   - Set `OPENAI_API_KEY` (and other values as needed).
3. Run:
   - `poetry run uvicorn app.main:app --reload`
4. Docs: `http://localhost:8000/docs`

## Frontend quickstart

1. Install (requires Bun):
   - `cd frontend`
   - `bun install`
2. Run dev server:
   - `bun dev`
3. Point the UI to the backend API (default `http://localhost:8000`); update env/config in the frontend as you build features.

## Key environment variables (`backend/env.example`)

- `APP_NAME` / `APP_DESCRIPTION`: Shown in FastAPI docs.
- `OPENAI_API_KEY`, `OPENAI_API_BASE`, `OPENAI_MODEL`, `OPENAI_EMBEDDING_MODEL`: OpenAI credentials/models.
- `CHROMA_DATABASE`, `CHROMA_COLLECTION_NAME`: ChromaDB storage/collection.
- `DATA_DIRECTORY`: Where uploaded/source documents are stored.

## API overview

- `GET /health`: Health check.
- `POST /upload`: Upload a document to be chunked and indexed into ChromaDB.
- `POST /chat`: Retrieval + generation over indexed docs.

## Data locations

- Chroma DB: `backend/data/chroma`
- Uploaded/source docs: `backend/data/documents`

## Notes

- Keep your secrets in `backend/.env` (ignored by git).
- Defaults in code can be overridden via `.env`. Align app metadata there as needed.
