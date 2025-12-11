"""Chat endpoint backed by RAG retrieval."""

from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse, SourceChunk
from app.services.rag import answer_question

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    answer, documents = answer_question(request.question, top_k=request.top_k)
    sources = [
        SourceChunk(content=doc.page_content, metadata=doc.metadata or {})
        for doc in documents
    ]
    return ChatResponse(answer=answer, sources=sources)
