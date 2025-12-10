"""Document loaders for various sources."""

from typing import List, Optional
from pathlib import Path
from langchain_community.document_loaders import (
    WebBaseLoader,
    PyPDFLoader,
    TextLoader,
)

# Optional import for unstructured loader (not available for Python 3.12+)
try:
    from langchain_community.document_loaders import UnstructuredFileLoader
    HAS_UNSTRUCTURED = True
except ImportError:
    HAS_UNSTRUCTURED = False
from langchain_core.documents import Document
import structlog

logger = structlog.get_logger()


class DocumentLoader:
    """Load documents from various sources (website, PDFs, text files)."""

    @staticmethod
    def load_from_url(url: str) -> List[Document]:
        """Load documents from a website URL."""
        try:
            logger.info("Loading documents from URL", url=url)
            loader = WebBaseLoader(url)
            documents = loader.load()
            logger.info("Successfully loaded documents from URL", url=url, count=len(documents))
            return documents
        except Exception as e:
            logger.error("Failed to load documents from URL", url=url, error=str(e))
            raise

    @staticmethod
    def load_from_pdf(file_path: str) -> List[Document]:
        """Load documents from a PDF file."""
        try:
            logger.info("Loading documents from PDF", file_path=file_path)
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            logger.info("Successfully loaded documents from PDF", file_path=file_path, count=len(documents))
            return documents
        except Exception as e:
            logger.error("Failed to load documents from PDF", file_path=file_path, error=str(e))
            raise

    @staticmethod
    def load_from_text(file_path: str) -> List[Document]:
        """Load documents from a text file."""
        try:
            logger.info("Loading documents from text file", file_path=file_path)
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load()
            logger.info("Successfully loaded documents from text file", file_path=file_path, count=len(documents))
            return documents
        except Exception as e:
            logger.error("Failed to load documents from text file", file_path=file_path, error=str(e))
            raise

    @staticmethod
    def load_from_directory(directory_path: str, pattern: str = "*.pdf") -> List[Document]:
        """Load all documents from a directory matching a pattern."""
        documents = []
        directory = Path(directory_path)
        
        if not directory.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")
        
        files = list(directory.glob(pattern))
        logger.info("Found files to load", directory=directory_path, pattern=pattern, count=len(files))
        
        for file_path in files:
            try:
                if file_path.suffix.lower() == ".pdf":
                    docs = DocumentLoader.load_from_pdf(str(file_path))
                elif file_path.suffix.lower() in [".txt", ".md"]:
                    docs = DocumentLoader.load_from_text(str(file_path))
                else:
                    # Try unstructured loader for other file types (if available)
                    if HAS_UNSTRUCTURED:
                        loader = UnstructuredFileLoader(str(file_path))
                        docs = loader.load()
                    else:
                        logger.warning(
                            "Unstructured loader not available. Skipping file",
                            file_path=str(file_path),
                            suffix=file_path.suffix
                        )
                        continue
                
                documents.extend(docs)
                logger.info("Loaded file", file_path=str(file_path), chunks=len(docs))
            except Exception as e:
                logger.warning("Failed to load file", file_path=str(file_path), error=str(e))
                continue
        
        logger.info("Total documents loaded from directory", directory=directory_path, count=len(documents))
        return documents

    @staticmethod
    def load_from_urls(urls: List[str]) -> List[Document]:
        """Load documents from multiple URLs."""
        all_documents = []
        for url in urls:
            try:
                documents = DocumentLoader.load_from_url(url)
                all_documents.extend(documents)
            except Exception as e:
                logger.warning("Failed to load URL", url=url, error=str(e))
                continue
        return all_documents