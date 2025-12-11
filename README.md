# BiasharaPlus RAG API

FastAPI-based Retrieval-Augmented Generation service using LangChain, ChromaDB, and OpenAI (or compatible) models. Inspired by the LangChain + Chroma pipeline from Sourav Ghosh's guide.

## Features

- Index: upsert documents with automatic chunking and embeddings.
- Retrieve: similarity search over Chroma.
- Generate: RAG pipeline combining retrieved context with ChatOpenAI.
- Config via env variables; structured logging; Docker + docker-compose.

## Quickstart

1. Copy environment file and set secrets:
   ```bash
   cp env.example .env
   # set OPENAI_API_KEY and (optionally) OPENAI_API_BASE/OPENAI_MODEL
   ```
2. Install dependencies (Poetry):
   ```bash
   poetry install
   ```
3. Run API locally:
   ```bash
   uvicorn app.main:app --reload
   ```
   Open http://localhost:8000/docs for interactive OpenAPI.

## API

- `GET /health`: service heartbeat.
- `POST /documents/upload`: upload a `.pdf` or `.txt` file. The file is chunked, embedded with OpenAI, and stored in Chroma.
- `POST /chat/`: ask a question. Returns an answer plus the retrieved source chunks.

## Notes

- Vector store persistence lives under `./data/chroma` by default. Uploaded source files are saved to `./data/documents`.
- Set `OPENAI_API_KEY` (and optionally `OPENAI_API_BASE`) in `.env` before running.
