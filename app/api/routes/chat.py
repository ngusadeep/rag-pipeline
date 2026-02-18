"""Chat endpoint backed by RAG retrieval."""

from fastapi import APIRouter, HTTPException

from app.models.schemas import ChatRequest, ChatResponse, SourceChunk
from app.services.rag import answer_question

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        answer, documents = answer_question(request.question, top_k=request.top_k)
        sources = [
            SourceChunk(content=doc.page_content, metadata=doc.metadata or {})
            for doc in documents
        ]
        return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"RAG error: {str(e)}")
