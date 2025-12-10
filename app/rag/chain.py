"""RAG chain for question-answering."""

from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from app.rag.retriever import RAGRetriever
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class RAGChain:
    """RAG chain that combines retrieval and generation."""

    def __init__(self, retriever: Optional[RAGRetriever] = None):
        """Initialize the RAG chain.
        
        Args:
            retriever: Optional RAGRetriever instance
        """
        self.retriever = retriever or RAGRetriever()
        
        # Initialize LLM with temperature 0.0 for factual answers
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            api_key=settings.openai_api_key,
        )
        
        # Create prompt template for grounded answers
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful customer support assistant for BiasharaPlus. 
Answer the user's question based ONLY on the provided context from BiasharaPlus documentation. 
If the answer cannot be found in the context, say "I don't have information about that in our documentation. Please contact our support team for assistance."

Context: {context}"""),
            ("human", "{input}"),
        ])
        
        # Create document chain
        document_chain = create_stuff_documents_chain(self.llm, self.prompt)
        
        # Create retrieval chain
        retriever_obj = self.retriever.vector_store.as_retriever(
            search_kwargs={"k": settings.top_k_retrieval}
        )
        self.qa_chain = create_retrieval_chain(retriever_obj, document_chain)
        
        logger.info("RAGChain initialized", model=settings.llm_model, temperature=settings.llm_temperature)

    def query(self, question: str) -> dict:
        """Query the RAG chain with a question.
        
        Args:
            question: User question
            
        Returns:
            Dictionary with 'answer' and 'context' (source documents)
        """
        logger.info("Processing query", question=question[:50])
        
        result = self.qa_chain.invoke({"input": question})
        
        logger.info(
            "Query processed",
            question=question[:50],
            answer_length=len(result.get("answer", "")),
            sources_count=len(result.get("context", [])),
        )
        
        return {
            "answer": result.get("answer", ""),
            "source_documents": result.get("context", []),
        }

    def query_with_sources(self, question: str) -> dict:
        """Query the RAG chain and format sources.
        
        Args:
            question: User question
            
        Returns:
            Dictionary with 'answer' and formatted 'sources'
        """
        result = self.query(question)
        
        # Format sources from documents
        sources = []
        for doc in result["source_documents"]:
            source_info = {
                "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "metadata": doc.metadata,
            }
            sources.append(source_info)
        
        return {
            "answer": result["answer"],
            "sources": sources,
        }

