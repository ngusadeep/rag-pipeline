"""Embedding service for vector generation."""

from typing import List, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone as PineconeVectorStore
from langchain_core.documents import Document
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class EmbeddingService:
    """Service for generating embeddings and managing Pinecone vector store."""

    def __init__(self):
        """Initialize the embedding service."""
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.openai_api_key,
        )
        
        logger.info("EmbeddingService initialized")

    def get_vector_store(self, index_name: Optional[str] = None) -> PineconeVectorStore:
        """Get or create a Pinecone vector store.
        
        Args:
            index_name: Name of the Pinecone index (default from settings)
            
        Returns:
            PineconeVectorStore instance
        """
        index_name = index_name or settings.pinecone_index_name
        
        logger.info("Getting Pinecone vector store", index_name=index_name)
        
        # Create vector store - PineconeVectorStore will handle index creation if needed
        vector_store = PineconeVectorStore(
            index_name=index_name,
            embedding=self.embeddings,
            pinecone_api_key=settings.pinecone_api_key,
        )
        
        return vector_store

    def add_documents(
        self,
        documents: List[Document],
        index_name: Optional[str] = None,
        namespace: Optional[str] = None,
    ) -> List[str]:
        """Add documents to the vector store.
        
        Args:
            documents: List of documents to add
            index_name: Name of the Pinecone index
            namespace: Optional namespace for the index
            
        Returns:
            List of document IDs
        """
        logger.info("Adding documents to vector store", count=len(documents))
        
        vector_store = self.get_vector_store(index_name)
        ids = vector_store.add_documents(documents, namespace=namespace)
        
        logger.info("Documents added to vector store", count=len(ids))
        return ids

    def delete_all(self, index_name: Optional[str] = None, namespace: Optional[str] = None):
        """Delete all vectors from the index.
        
        Args:
            index_name: Name of the Pinecone index
            namespace: Optional namespace for the index
        """
        logger.warning("Deleting all vectors from index", index_name=index_name or settings.pinecone_index_name)
        
        vector_store = self.get_vector_store(index_name)
        # Delete all vectors using the vector store's delete method
        # Note: This may require iterating through all vectors
        # For now, we'll use the vector store's delete method if available
        try:
            # Try to get the underlying index and delete all
            if hasattr(vector_store, 'index'):
                vector_store.index.delete(delete_all=True, namespace=namespace)
            elif hasattr(vector_store, '_index'):
                vector_store._index.delete(delete_all=True, namespace=namespace)
            else:
                logger.warning("Cannot delete all vectors - index access not available. Consider using Pinecone console.")
        except Exception as e:
            logger.error("Error deleting vectors", error=str(e))
            raise
        
        logger.info("All vectors deleted from index")

