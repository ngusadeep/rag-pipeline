"""Retriever for semantic search."""

from typing import List, Optional
from langchain_core.documents import Document
from langchain_pinecone import PineconeVectorStore
from app.rag.embeddings import EmbeddingService
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class RAGRetriever:
    """Retriever for fetching relevant documents from vector store."""

    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        """Initialize the retriever.
        
        Args:
            embedding_service: Optional EmbeddingService instance
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_store = self.embedding_service.get_vector_store()
        self.top_k = settings.top_k_retrieval
        
        logger.info("RAGRetriever initialized", top_k=self.top_k)

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Document]:
        """Retrieve relevant documents for a query.
        
        Args:
            query: User query string
            top_k: Number of documents to retrieve (default from settings)
            
        Returns:
            List of relevant documents
        """
        top_k = top_k or self.top_k
        
        logger.info("Retrieving documents", query=query[:50], top_k=top_k)
        
        # Use similarity search to retrieve relevant documents
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": top_k},
        )
        
        documents = retriever.get_relevant_documents(query)
        
        logger.info(
            "Documents retrieved",
            query=query[:50],
            count=len(documents),
        )
        
        return documents

    def retrieve_with_scores(
        self, query: str, top_k: Optional[int] = None
    ) -> List[tuple[Document, float]]:
        """Retrieve relevant documents with similarity scores.
        
        Args:
            query: User query string
            top_k: Number of documents to retrieve
            
        Returns:
            List of tuples (document, score)
        """
        top_k = top_k or self.top_k
        
        logger.info("Retrieving documents with scores", query=query[:50], top_k=top_k)
        
        # Use similarity search with scores
        documents_with_scores = self.vector_store.similarity_search_with_score(
            query, k=top_k
        )
        
        logger.info(
            "Documents retrieved with scores",
            query=query[:50],
            count=len(documents_with_scores),
        )
        
        return documents_with_scores

