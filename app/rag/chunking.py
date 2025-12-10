"""Text chunking for document processing."""

from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class TextChunker:
    """Split documents into manageable chunks for embedding."""

    def __init__(
        self,
        chunk_size: Optional[int] = None,
        chunk_overlap: Optional[int] = None,
    ):
        """Initialize the text chunker.
        
        Args:
            chunk_size: Maximum size of each chunk (default from settings)
            chunk_overlap: Overlap between chunks (default from settings)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        
        logger.info(
            "TextChunker initialized",
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks.
        
        Args:
            documents: List of documents to chunk
            
        Returns:
            List of chunked documents
        """
        logger.info("Chunking documents", document_count=len(documents))
        
        chunks = self.splitter.split_documents(documents)
        
        logger.info(
            "Documents chunked successfully",
            original_count=len(documents),
            chunk_count=len(chunks),
        )
        
        return chunks

    def chunk_text(self, text: str, metadata: Optional[dict] = None) -> List[Document]:
        """Split a single text string into chunks.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to chunks
            
        Returns:
            List of chunked documents
        """
        document = Document(page_content=text, metadata=metadata or {})
        return self.chunk_documents([document])