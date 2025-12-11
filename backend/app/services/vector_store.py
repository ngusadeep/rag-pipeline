"""Chroma vector store helpers."""

from pathlib import Path
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from app.core.config import get_settings

_vector_store: Optional[Chroma] = None
_embeddings: Optional[OpenAIEmbeddings] = None


def get_embeddings() -> OpenAIEmbeddings:
    """Singleton embeddings client."""
    global _embeddings
    if _embeddings is None:
        settings = get_settings()
        _embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_api_base,
        )
    return _embeddings


def get_vector_store() -> Chroma:
    """Singleton persistent Chroma instance."""
    global _vector_store
    if _vector_store is None:
        settings = get_settings()
        persist_dir: Path = settings.chroma_path
        persist_dir.mkdir(parents=True, exist_ok=True)
        _vector_store = Chroma(
            collection_name=settings.chroma_collection_name,
            embedding_function=get_embeddings(),
            persist_directory=str(persist_dir),
        )
    return _vector_store


def add_texts(chunks: List[str], metadatas: Optional[List[dict]] = None) -> int:
    """Add text chunks to vector store."""
    vector_store = get_vector_store()
    vector_store.add_texts(chunks, metadatas=metadatas)
    return len(chunks)


def search(query: str, *, k: int = 4):
    """Similarity search over stored documents."""
    return get_vector_store().similarity_search(query, k=k)
