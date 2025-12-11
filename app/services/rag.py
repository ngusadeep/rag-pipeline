from typing import List

from langchain.docstore.document import Document
from langchain_openai import ChatOpenAI

from app.core.config import get_settings
from app.core.logging_config import get_logger
from app.models.schemas import (
    DocumentInput,
    GenerationRequest,
    GenerationResponse,
    QueryRequest,
    QueryResponse,
    RetrievalResult,
)
from app.utils.prompts import get_rag_prompt
from app.utils.text import get_text_splitter
from .vector_store import similarity_search, upsert_documents

logger = get_logger(__name__)


def _split_documents(doc_inputs: List[DocumentInput]) -> List[Document]:
    splitter = get_text_splitter()
    documents: List[Document] = []
    for doc in doc_inputs:
        chunks = splitter.create_documents(
            texts=[doc.text],
            metadatas=[{"id": doc.id, **(doc.metadata or {})}],
        )
        documents.extend(chunks)
    return documents


def index_documents(payload: List[DocumentInput]) -> int:
    docs = _split_documents(payload)
    return upsert_documents(docs)


def retrieve(payload: QueryRequest) -> QueryResponse:
    matches = similarity_search(payload.query, k=payload.k)
    results: List[RetrievalResult] = []
    for doc, score in matches:
        results.append(
            RetrievalResult(
                id=str(doc.metadata.get("id")),
                text=doc.page_content,
                metadata=doc.metadata,
                score=score,
            )
        )
    return QueryResponse(results=results)


def _get_chat_model() -> ChatOpenAI:
    settings = get_settings()
    chat_kwargs = {}
    if settings.openai_api_base:
        chat_kwargs["base_url"] = settings.openai_api_base
    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=0.1,
        **chat_kwargs,
    )


def generate(payload: GenerationRequest) -> GenerationResponse:
    query_response = retrieve(payload)
    prompt = get_rag_prompt()
    context = "\n\n".join(
        f"[{res.id}] {res.text}" for res in query_response.results
    )

    llm = _get_chat_model()
    chain = prompt | llm
    answer = chain.invoke({"context": context, "question": payload.query})
    logger.info("Generated answer for query")
    return GenerationResponse(
        answer=answer.content, citations=query_response.results
    )
