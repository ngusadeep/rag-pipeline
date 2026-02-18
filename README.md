<<<<<<< HEAD
# Basic RAG Pipeline (LangChain + OpenAI + Zvec)
=======
# Retreival Augmented Generation RAG Pipeline (LangChain + OpenAI + Zvec Vector DB )
>>>>>>> 905db41fe6e4df0511b24dc1ceddb51659fae62c

Minimal Retrieval-Augmented Generation stack: FastAPI backend with LangChain + [Zvec](https://github.com/alibaba/zvec) (in-process vector DB) + OpenAI, plus a Next.js frontend scaffold you can wire up to the API.

## Project structure

```
backend/    # FastAPI + LangChain + Zvec API (Poetry)
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
- `ZVEC_DATABASE`, `ZVEC_COLLECTION_NAME`: Zvec collection path and name.
- `EMBEDDING_DIMENSION`: Vector size (default 1536 for `text-embedding-3-small`).
- `DATA_DIRECTORY`: Where uploaded/source documents are stored.

## API overview

- `GET /health`: Health check.
- `POST /upload`: Upload a document to be chunked and indexed into Zvec.
- `POST /chat`: Retrieval + generation over indexed docs.

## Data locations

- Zvec collection: `backend/data/zvec/<ZVEC_COLLECTION_NAME>`
- Uploaded/source docs: `backend/data/documents`

## Notes

- **Zvec supports Linux (x86_64, ARM64) and macOS (ARM64) only.** On Windows, run the backend in [WSL](https://docs.microsoft.com/en-us/windows/wsl/) or Docker.
- Keep your secrets in `backend/.env` (ignored by git).
- Defaults in code can be overridden via `.env`. Align app metadata there as needed.
