# BiasharaPlus RAG API

FastAPI-based Retrieval-Augmented Generation service using LangChain, ChromaDB, and OpenAI (or compatible) models.

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

### With Docker Compose

```bash
docker-compose up --build
```

Chroma persists to `data/chroma`. Update `.env` for model keys.

## API

- `GET /api/health` — service health.
- `POST /api/index` — body `{ "documents": [ { "id": "...", "text": "...", "metadata": {...} } ] }`.
- `POST /api/retrieve` — body `{ "query": "...", "k": 4 }`.
- `POST /api/generate` — body `{ "query": "...", "k": 4 }`.

## Project Structure

- `app/main.py` — FastAPI app entry.
- `app/api/routes/` — route modules for health, index, retrieve, generate.
- `app/services/rag.py` — RAG orchestration (index/retrieve/generate).
- `app/services/vector_store.py` — Chroma + embeddings management.
- `app/core/config.py` — Pydantic settings from env.
- `app/core/logging_config.py` — structured logging.
- `app/models/schemas.py` — request/response models.
- `app/utils/prompts.py` — shared prompt templates.
- `app/utils/text.py` — text splitter helpers.
- `app/utils/chroma_connection.py` — optional Chroma client/collection dependency.
- `app/api/routes/index_from_url.py` — index a document by fetching from URL.
- `data/` — persisted vector store and docs (gitkept).
- `env.example` — sample environment variables.

### Optional startup bootstrap indexing

- Set `BOOTSTRAP_DOCUMENT_URL` and `BOOTSTRAP_DOCUMENT_ID` (and optional `BOOTSTRAP_DOCUMENT_SOURCE`) in `.env`. On startup, the service will fetch that URL (PDF or text), extract content, and index it into Chroma automatically.

### Indexing from GitHub (PDF or text)

- `POST /api/index_from_url` now fetches the URL. If the content is PDF (by content-type or `.pdf` suffix), it extracts text with `pypdf` first, then indexes. For text URLs it decodes UTF-8.
- Example:
  ```bash
  curl -X POST http://localhost:8000/api/index_from_url \
    -H "Content-Type: application/json" \
    -d '{
      "id": "biashara-plus-pdf",
      "url": "https://raw.githubusercontent.com/ngusadeep/bplus-docs/main/Biashara%20Plus.pdf",
      "metadata": { "source": "github" }
    }'
  ```

### Chroma local vs cloud

- Local (default): set `CHROMA_PERSIST_DIRECTORY`, leave `CHROMA_API_KEY` unset.
- Cloud: set `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE`, and `CHROMA_COLLECTION_NAME`. The app will auto-use Chroma Cloud.

## Notes

- Uses `RecursiveCharacterTextSplitter` (800/100 overlap).
- Uses `ChatOpenAI` and `OpenAIEmbeddings`; set `OPENAI_API_BASE` for OpenAI-compatible providers.
- Keep `CHROMA_PERSIST_DIRECTORY` mounted when using containers to retain embeddings.
