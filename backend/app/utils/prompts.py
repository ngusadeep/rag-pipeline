"""Prompt templates for the RAG pipeline."""

from langchain_core.prompts import ChatPromptTemplate

rag_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a helpful assistant that answers using the provided context. "
                "If the context does not contain the answer, say you do not know. "
                "Be concise and prefer bullet points when listing items."
            ),
        ),
        (
            "human",
            "Question: {input}\n\nContext:\n{context}\n\nAnswer:",
        ),
    ]
)
