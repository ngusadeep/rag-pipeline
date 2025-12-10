"""Agentic RAG implementation using LangChain tools."""

from typing import List, Optional

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from app.core.config import settings
from app.rag.retriever import RAGRetriever
import structlog

logger = structlog.get_logger()


class RAGAgent:
    """Agentic RAG that lets the LLM decide when to retrieve context."""

    def __init__(self, retriever: Optional[RAGRetriever] = None):
        """Initialize the RAG agent.

        Args:
            retriever: Optional retriever instance
        """
        self.retriever = retriever or RAGRetriever()
        self.top_k = settings.top_k_retrieval
        self._last_docs: List[Document] = []

        # Initialize LLM (tool-calling ready)
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            api_key=settings.openai_api_key,
        )

        # Define retrieval tool - create a closure to access self
        def _retrieve_context(query: str) -> str:
            """Retrieve relevant BiasharaPlus documentation for a query.
            
            Args:
                query: The search query to find relevant documentation
                
            Returns:
                Serialized context with source metadata and content
            """
            docs = self.retriever.vector_store.similarity_search(query, k=self.top_k)
            self._last_docs = docs
            serialized = "\n\n".join(
                f"Source: {doc.metadata}\nContent: {doc.page_content}"
                for doc in docs
            )
            return serialized

        # Wrap the function as a tool
        retrieve_context_tool = tool(_retrieve_context)
        self.tools = [retrieve_context_tool]

        # Prompt aligns with LangChain agentic RAG docs
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You are a helpful customer support assistant for BiasharaPlus. "
                        "Use the retrieval tool when you need context. "
                        'If the answer is not in the documentation, say '
                        '"I don\'t have information about that in our documentation."'
                    ),
                ),
                ("placeholder", "{chat_history}"),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=False,
            return_intermediate_steps=False,
        )

        logger.info("RAGAgent initialized", mode="agentic", model=settings.llm_model)

    def query_with_sources(self, question: str) -> dict:
        """Run the agent and return answer plus sources."""
        # Reset last docs for this run
        self._last_docs = []
        result = self.executor.invoke({"input": question, "chat_history": []})
        answer = result.get("output", "")

        sources = []
        for doc in self._last_docs:
            sources.append(
                {
                    "content": (
                        doc.page_content[:200] + "..."
                        if len(doc.page_content) > 200
                        else doc.page_content
                    ),
                    "metadata": doc.metadata,
                }
            )

        logger.info(
            "Agent query processed",
            question=question[:50],
            answer_length=len(answer),
            sources_count=len(sources),
        )

        return {"answer": answer, "sources": sources}

