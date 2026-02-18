"""Zvec vector store with LangChain VectorStore interface."""

import uuid
from pathlib import Path
from typing import Any, List, Optional

import zvec
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore
from langchain_openai import OpenAIEmbeddings

from app.core.config import get_settings

_embedding_dimension = 1536  # OpenAI text-embedding-3-small

_vector_store: Optional["ZvecVectorStore"] = None
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


def _make_zvec_schema(dimension: int, collection_name: str) -> zvec.CollectionSchema:
    return zvec.CollectionSchema(
        name=collection_name,
        fields=[
            zvec.FieldSchema(name="content", data_type=zvec.DataType.STRING),
            zvec.FieldSchema(name="source", data_type=zvec.DataType.STRING),
            zvec.FieldSchema(name="chunk", data_type=zvec.DataType.INT64),
        ],
        vectors=[
            zvec.VectorSchema(
                name="embedding",
                data_type=zvec.DataType.VECTOR_FP32,
                dimension=dimension,
                index_param=zvec.HnswIndexParam(metric_type=zvec.MetricType.COSINE),
            ),
        ],
    )


def _get_or_create_collection(path: Path, schema: zvec.CollectionSchema):
    path.mkdir(parents=True, exist_ok=True)
    try:
        return zvec.open(str(path))
    except Exception:
        return zvec.create_and_open(path=str(path), schema=schema)


class ZvecVectorStore(VectorStore):
    """LangChain VectorStore backed by Zvec (in-process vector DB)."""

    def __init__(
        self,
        collection: Any,
        embedding: Embeddings,
        *,
        vector_field: str = "embedding",
        content_field: str = "content",
        metadata_fields: Optional[List[str]] = None,
    ):
        self._collection = collection
        self._embedding = embedding
        self._vector_field = vector_field
        self._content_field = content_field
        self._metadata_fields = metadata_fields or ["source", "chunk"]

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[str]:
        if not texts:
            return []
        metadatas = metadatas or [{}] * len(texts)
        if len(metadatas) != len(texts):
            raise ValueError("metadatas length must match texts length")
        ids = ids or [str(uuid.uuid4()) for _ in texts]
        if len(ids) != len(texts):
            raise ValueError("ids length must match texts length")

        embeddings = self._embedding.embed_documents(texts)
        docs = []
        for i, (text, meta, doc_id) in enumerate(zip(texts, metadatas, ids)):
            docs.append(
                zvec.Doc(
                    id=doc_id,
                    vectors={self._vector_field: embeddings[i]},
                    fields={
                        self._content_field: text,
                        "source": meta.get("source", ""),
                        "chunk": int(meta.get("chunk", i)),
                    },
                )
            )
        self._collection.insert(docs)
        return ids

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Optional[dict] = None,
        **kwargs: Any,
    ) -> List[Document]:
        scored = self.similarity_search_with_score(query, k=k, **kwargs)
        return [doc for doc, _ in scored]

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        **kwargs: Any,
    ) -> List[tuple[Document, float]]:
        query_embedding = self._embedding.embed_query(query)
        results = self._collection.query(
            vectors=zvec.VectorQuery(
                field_name=self._vector_field,
                vector=query_embedding,
            ),
            topk=k,
        )
        out = []
        for hit in results:
            if not hasattr(hit, "fields") or hit.fields is None:
                continue
            content = hit.fields.get(self._content_field, "")
            metadata = {
                "source": hit.fields.get("source", ""),
                "chunk": hit.fields.get("chunk", 0),
            }
            score = float(hit.score if hit.score is not None else 0.0)
            out.append((Document(page_content=content, metadata=metadata), score))
        return out

    @classmethod
    def __get_pydantic_fields_set__(cls) -> set:
        return set()


def get_vector_store() -> ZvecVectorStore:
    """Singleton Zvec-backed vector store."""
    global _vector_store
    if _vector_store is None:
        settings = get_settings()
        path: Path = settings.zvec_path
        dim = getattr(settings, "embedding_dimension", _embedding_dimension)
        schema = _make_zvec_schema(dim, settings.zvec_collection_name)
        collection = _get_or_create_collection(path, schema)
        _vector_store = ZvecVectorStore(
            collection=collection,
            embedding=get_embeddings(),
        )
    return _vector_store


def add_texts(chunks: List[str], metadatas: Optional[List[dict]] = None) -> int:
    """Add text chunks to vector store."""
    store = get_vector_store()
    store.add_texts(chunks, metadatas=metadatas)
    return len(chunks)


def search(query: str, *, k: int = 4) -> List[Document]:
    """Similarity search over stored documents."""
    return get_vector_store().similarity_search(query, k=k)
