from typing import List

from langchain.docstore.document import Document
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

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
from .vector_store import get_retriever, similarity_search, upsert_documents
from urllib import parse, request
from io import BytesIO
from pypdf import PdfReader

logger = get_logger(__name__)


def _normalize_github_url(url: str) -> str:
    """Convert GitHub blob URLs to raw URLs so binary files fetch correctly."""
    try:
        parsed = parse.urlparse(url)
        if parsed.netloc == "github.com" and "/blob/" in parsed.path:
            new_path = parsed.path.replace("/blob/", "/", 1)
            return parse.urlunparse(
                parsed._replace(netloc="raw.githubusercontent.com", path=new_path)
            )
    except Exception:
        # Fallback to original URL if normalization fails.
        return url
    return url


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
    """Generate an answer using the notebook-style RAG chain (retriever → prompt → LLM)."""
    retriever = get_retriever(payload.k)

    def _format_docs(docs: List[Document]) -> str:
        return "\n\n".join(
            f"[{doc.metadata.get('id')}] {doc.page_content}" for doc in docs
        )

    prompt = get_rag_prompt()
    llm = _get_chat_model()
    chain = (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    answer_text = chain.invoke(payload.query)
    # Also return structured citations from a similarity search.
    query_response = retrieve(payload)
    logger.info("Generated answer for query")
    return GenerationResponse(
        answer=answer_text, citations=query_response.results
    )
