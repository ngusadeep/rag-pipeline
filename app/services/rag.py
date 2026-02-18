"""RAG pipeline: ingestion, retrieval, and answer generation."""

from pathlib import Path
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from pypdf import PdfReader

from app.core.config import get_settings
from app.services.vector_store import add_texts, get_vector_store
from app.utils.prompts import rag_prompt
from app.utils.text import chunk_text


def get_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_api_base,
        temperature=0,
    )


def ingest_text(text: str, source: str) -> int:
    """Split raw text and store in Zvec with metadata."""
    chunks = chunk_text(text)
    metadatas = [{"source": source, "chunk": idx} for idx, _ in enumerate(chunks)]
    return add_texts(chunks, metadatas=metadatas)


def ingest_file(path: Path) -> int:
    """Load file content (PDF or text) and ingest."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        reader = PdfReader(path)
        pages = [page.extract_text() or "" for page in reader.pages]
        text = "\n\n".join(pages)
    else:
        text = path.read_text(encoding="utf-8")
    return ingest_text(text, source=path.name)


def get_retrieval_chain(top_k: int = 4):
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | rag_prompt
        | get_llm()
    )
    return chain


def answer_question(question: str, top_k: int = 4) -> Tuple[str, List[Document]]:
    """Run RAG chain and return answer plus source documents."""
    chain = get_retrieval_chain(top_k=top_k)
    vector_store = get_vector_store()
    retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
    sources = retriever.invoke(question)
    response = chain.invoke(question)
    answer = response.content if hasattr(response, "content") else str(response)
    return answer, sources
