# BiasharaPlus Customer Support AI Agent

A production-ready RAG (Retrieval-Augmented Generation) system for automated customer support using LangChain, OpenAI, and Pinecone.

## Features

- **Document Ingestion**: Load content from websites, PDFs, and text files
- **Semantic Search**: Pinecone vector database for efficient retrieval
- **RAG Chain**: Combines retrieval with OpenAI LLM for accurate, source-grounded answers
- **FastAPI Backend**: RESTful API with `/ask` endpoint for queries
- **Admin Panel**: Authentication and document reindexing capabilities
- **Audit Logging**: Track all queries and indexing operations in PostgreSQL
- **Source Tracking**: Every answer includes references to source documents

## Architecture

```
┌─────────────┐
│   FastAPI   │
│   Backend   │
└──────┬──────┘
       │
       ├─── Query Service ───> RAG Chain ───> Retriever ───> Pinecone
       │
       └─── Admin Routes ───> Indexing Service ───> Document Loaders
```

## Project Structure

```
backend/
├── app/
│   ├── core/           # Core configuration and database
│   │   ├── config.py   # Settings loaded from .env
│   │   ├── database.py # Database session management
│   │   ├── logging.py  # Structured logging
│   │   └── deps.py     # FastAPI dependencies
│   ├── models/         # SQLAlchemy database models
│   │   ├── admin.py    # AdminUser model
│   │   └── logs.py     # QueryLog and IndexingLog models
│   ├── schemas/        # Pydantic request/response schemas
│   │   ├── query.py    # Query schemas
│   │   ├── admin.py    # Admin schemas
│   │   └── reindex.py  # Reindexing schemas
│   ├── rag/            # RAG components
│   │   ├── loaders.py  # Document loaders (website, PDF, text)
│   │   ├── chunking.py # Text chunking
│   │   ├── embeddings.py # Embedding service and Pinecone integration
│   │   ├── retriever.py # Semantic search retriever
│   │   └── chain.py    # RAG chain with OpenAI LLM
│   ├── services/       # Business logic services
│   │   ├── auth.py     # Authentication service
│   │   ├── indexing.py # Document indexing service
│   │   └── query.py    # Query processing service
│   ├── routes/         # FastAPI route handlers
│   │   ├── query.py    # /ask endpoint
│   │   └── admin.py    # /admin endpoints
│   └── main.py         # FastAPI application
├── pyproject.toml      # Poetry dependencies
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
└── .env               # Environment variables (create from .env.example)
```

## Setup

### Prerequisites

- Python 3.11+
- Poetry
- PostgreSQL (or use Docker Compose)
- OpenAI API key
- Pinecone API key and index

### Installation

1. **Clone the repository**

   ```bash
   cd backend
   ```

2. **Install dependencies with Poetry**

   ```bash
   poetry install
   ```

3. **Create `.env` file**

   Create a `.env` file in the project root with the following variables:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX_NAME=biasharaplus-rag
   PINECONE_ENVIRONMENT=us-east-1-aws
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bplus_rag_db
   SECRET_KEY=your_secret_key_here
   ```

   **Generate a secure SECRET_KEY:**

   Use the provided script:

   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   Copy the generated key to your `.env` file as `SECRET_KEY=...`

4. **Set up database**

   ```bash
   # Using Docker Compose (recommended)
   docker-compose up -d db

   # Or use existing PostgreSQL instance
   # Update DATABASE_URL in .env
   ```

5. **Run database migrations** (tables are auto-created on startup)

6. **Start the application**

   ```bash
   poetry run uvicorn app.main:app --reload
   ```

   Or using Docker Compose:

   ```bash
   docker-compose up
   ```

## API Endpoints

### Query Endpoint

**POST `/ask`**

Ask a question about BiasharaPlus services.

Request:

```json
{
  "query": "How do I register on BiasharaPlus?"
}
```

Response:

```json
{
  "answer": "To register, visit the BiasharaPlus homepage...",
  "sources": [
    {
      "url": "https://biasharaplus.com/register",
      "title": "Registration Guide",
      "chunk_id": "chunk_123",
      "score": 0.95
    }
  ],
  "response_time_ms": 1234
}
```

### Admin Endpoints

**POST `/admin/login`**

Admin login (OAuth2 password flow).

Request (form data):

```
username: admin
password: admin123
```

Response:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**POST `/admin/reindex`**

Trigger document reindexing (requires authentication).

Headers:

```
Authorization: Bearer <access_token>
```

Request:

```json
{
  "source_type": "website",
  "force": false
}
```

Response:

```json
{
  "status": "success",
  "message": "Documents indexed successfully",
  "documents_processed": 10,
  "chunks_created": 45,
  "indexing_log_id": 1
}
```

## Usage

### 1. Index Documents

First, index your documents using the admin endpoint:

```bash
# Login to get token
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Use the token to reindex
curl -X POST "http://localhost:8000/admin/reindex" \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"source_type": "website", "force": true}'
```

### 2. Query the System

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I register?"}'
```

## Configuration

All configuration is loaded from `.env` file. Key settings:

- `CHUNK_SIZE`: Document chunk size (default: 800)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `TOP_K_RETRIEVAL`: Number of documents to retrieve (default: 5)
- `LLM_TEMPERATURE`: LLM temperature for factual answers (default: 0.0)
- `LLM_MODEL`: OpenAI model to use (default: gpt-4o-mini)
- `RAG_MODE`: Choose `chain` (fast, always retrieve) or `agent` (LangChain agentic RAG that decides when/how to retrieve; default: chain)

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black app/
poetry run ruff check app/
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Use a strong `SECRET_KEY`
3. Configure proper CORS origins
4. Use environment variables for sensitive data
5. Set up proper logging and monitoring
6. Use a production ASGI server (e.g., Gunicorn with Uvicorn workers)

## License

Copyright (c) 2025 Samwel Ngusa
