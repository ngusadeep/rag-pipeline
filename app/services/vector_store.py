from typing import Iterable, List
import uuid

from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from pinecone import Pinecone, ServerlessSpec

from app.core.config import get_settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


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


def _init_pinecone_index_if_needed(client: Pinecone, index_name: str, dim: int, cloud: str, region: str) -> None:
    index_list = client.list_indexes()
    try:
        names = index_list.names() if callable(getattr(index_list, "names", None)) else index_list.names
    except Exception:
        names = index_list if isinstance(index_list, list) else []
    if index_name in names:
        try:
            desc = client.describe_index(name=index_name)
            current_dim = desc.get("dimension") if isinstance(desc, dict) else getattr(desc, "dimension", None)
            if current_dim and current_dim != dim:
                logger.warning(
                    "Pinecone index %s dimension mismatch (found=%s, expected=%s); recreating",
                    index_name,
                    current_dim,
                    dim,
                )
                client.delete_index(name=index_name)
                names.remove(index_name)
        except Exception as exc:
            logger.warning("Could not describe Pinecone index %s: %s", index_name, exc)

    if index_name not in names:
        client.create_index(
            name=index_name,
            dimension=dim,
            metric="cosine",
            spec=ServerlessSpec(cloud=cloud, region=region),
        )
        logger.info("Created Pinecone index %s (dim=%s, cloud=%s, region=%s)", index_name, dim, cloud, region)


def get_vector_store() -> PineconeVectorStore:
    settings = get_settings()
    embeddings = get_embeddings()
    pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
    dim = len(embeddings.embed_query("ping"))
    _init_pinecone_index_if_needed(
        pinecone_client,
        settings.pinecone_index_name,
        dim,
        settings.pinecone_cloud,
        settings.pinecone_region,
    )
    logger.info("Using Pinecone (index=%s)", settings.pinecone_index_name)
    index = pinecone_client.Index(settings.pinecone_index_name)
    return PineconeVectorStore(index=index, embedding=embeddings)


def upsert_documents(documents: Iterable[Document]) -> int:
    vector_store = get_vector_store()
    ids: List[str] = []
    for doc in documents:
        doc_id = doc.metadata.get("id") if doc.metadata else None
        if doc_id:
            try:
                ids.append(str(uuid.UUID(str(doc_id))))
            except Exception:
                ids.append(str(uuid.uuid5(uuid.NAMESPACE_URL, str(doc_id))))
        else:
            ids.append(str(uuid.uuid4()))
    vector_store.add_documents(list(documents), ids=ids)
    logger.info("Upserted %s documents into Pinecone", len(ids))
    return len(ids)


def similarity_search(query: str, k: int = 4):
    vector_store = get_vector_store()
    return vector_store.similarity_search_with_score(query, k=k)
