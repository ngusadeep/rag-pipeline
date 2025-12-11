from pathlib import Path
from typing import Iterable, List

from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document

from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def _ensure_persist_dir(path: str) -> str:
    Path(path).mkdir(parents=True, exist_ok=True)
    return path


def get_embeddings() -> OpenAIEmbeddings:
    settings = get_settings()
    embed_kwargs = {}
    if settings.openai_api_base:
        embed_kwargs["base_url"] = settings.openai_api_base
    return OpenAIEmbeddings(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
        **embed_kwargs,
    )


def get_vector_store() -> Chroma:
    settings = get_settings()
    persist_directory = _ensure_persist_dir(settings.chroma_persist_directory)
    embeddings = get_embeddings()
    return Chroma(
        embedding_function=embeddings, persist_directory=persist_directory
    )


def upsert_documents(documents: Iterable[Document]) -> int:
    vector_store = get_vector_store()
    ids: List[str] = []
    for doc in documents:
        doc_id = doc.metadata.get("id") if doc.metadata else None
        ids.append(str(doc_id) if doc_id else None)
    vector_store.add_documents(list(documents), ids=ids)
    vector_store.persist()
    logger.info("Upserted %s documents into Chroma", len(ids))
    return len(ids)


def similarity_search(query: str, k: int = 4):
    vector_store = get_vector_store()
    return vector_store.similarity_search_with_score(query, k=k)
