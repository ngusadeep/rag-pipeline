# Basic RAG Pipeline (LangChain + OpenAI + ChromaDB)

This project is a minimal Retrieval-Augmented Generation (RAG) stack that uses FastAPI, LangChain, ChromaDB, and OpenAI to serve answers grounded in your own documents.

## Project structure

```
backend/   # FastAPI + LangChain + ChromaDB backend
frontend/  # Placeholder for UI; wire up to backend API when ready
```

## Backend quickstart

1. Install dependencies (Python 3.10+ recommended):
   - `cd backend`
   - `poetry install`
2. Configure environment:
   - Copy `env.example` to `.env`.
   - Set `OPENAI_API_KEY` and any other values (see below).
3. Run the API:
   - `poetry run uvicorn app.main:app --reload`
4. Access the docs at `http://localhost:8000/docs`.

## Key environment variables (`backend/env.example`)

- `APP_NAME` / `APP_DESCRIPTION`: Metadata shown in FastAPI docs.
- `OPENAI_API_KEY`, `OPENAI_API_BASE`, `OPENAI_MODEL`, `OPENAI_EMBEDDING_MODEL`: OpenAI credentials and models.
- `CHROMA_DATABASE`, `CHROMA_COLLECTION_NAME`: ChromaDB storage and collection.
- `DATA_DIRECTORY`: Where uploaded/source documents are stored.

## API overview

- `GET /health`: Service health check.
- `POST /upload`: Upload a document to be chunked and indexed into ChromaDB.
- `POST /chat`: Chat endpoint that runs retrieval + generation over indexed docs.

## Frontend

The `frontend/` directory is a placeholder for a future UI. Point it at the backend API once implemented.
