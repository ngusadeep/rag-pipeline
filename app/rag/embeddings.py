"""Embedding service for vector generation."""

from typing import List, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document
from pinecone import Pinecone, ServerlessSpec
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
        
        # Initialize Pinecone client
        self.pinecone_client = Pinecone(api_key=settings.pinecone_api_key)
        
        logger.info("EmbeddingService initialized")

    def get_vector_store(self, index_name: Optional[str] = None) -> PineconeVectorStore:
        """Get or create a Pinecone vector store.
        
        Args:
            index_name: Name of the Pinecone index (default from settings)
            
        Returns:
            PineconeVectorStore instance
        """
        index_name = index_name or settings.pinecone_index_name
        
        # Check if index exists, create if not
        if index_name not in [index.name for index in self.pinecone_client.list_indexes()]:
            logger.info("Creating new Pinecone index", index_name=index_name)
            self.pinecone_client.create_index(
                name=index_name,
                dimension=1536,  # text-embedding-3-small dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=settings.pinecone_environment,
                ),
            )
            logger.info("Pinecone index created", index_name=index_name)
        else:
            logger.info("Using existing Pinecone index", index_name=index_name)
        
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
        # Get all vector IDs and delete them
        index = self.pinecone_client.Index(index_name or settings.pinecone_index_name)
        index.delete(delete_all=True, namespace=namespace)
        
        logger.info("All vectors deleted from index")

