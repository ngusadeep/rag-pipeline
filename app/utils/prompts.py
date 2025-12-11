from langchain_core.prompts import ChatPromptTemplate

BASE_RAG_PROMPT = (
    "You are a helpful assistant for BiasharaPlus.\n"
    "Use the provided context to answer.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n"
    "Answer concisely."
)


def get_rag_prompt() -> ChatPromptTemplate:
    """Return the base RAG prompt template."""
    return ChatPromptTemplate.from_template(BASE_RAG_PROMPT)
