# RAG Pipeline (LangChain + OpenAI + Zvec)

Retrieval-Augmented Generation pipeline: FastAPI backend with LangChain + [Zvec](https://github.com/alibaba/zvec) (in-process vector DB) + OpenAI, plus a Next.js frontend you can wire up to the API.

## Project structure

```
backend/    # FastAPI + LangChain + Zvec API (Poetry)
frontend/   # Next.js app scaffold (Bun)
```

## Backend quickstart

### Option 1: Docker (Recommended)

1. Configure environment:
   - `cp env.example .env`
   - Set `OPENAI_API_KEY` (and other values as needed).
2. Run with Docker Compose:
   - `docker-compose up --build`
3. Docs: `http://localhost:8000/docs`

### Option 2: Local Development (Python 3.12+)

1. Install with uv (recommended):
   - `uv sync`
2. Or with pip:
   - `pip install -e .`
3. Configure environment:
   - `cp env.example .env`
   - Set `OPENAI_API_KEY` (and other values as needed).
4. Run:
   - `uvicorn app.main:app --reload`
   - Or with uv: `uv run uvicorn app.main:app --reload`
5. Docs: `http://localhost:8000/docs`

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
