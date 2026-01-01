from crewai.tools import tool
from rag import RAG

@tool("retrieve_security_policy")
def retrieve_security_policy(question: str) -> dict:
    """
    This is a tool for querying against the InfoSecurity policy.
    The purpose of this tool is to retrieve any related policies or guidelines based on the user's question.
    
    Args:
        question (str): The user's question or request related to InfoSecurity policies.

    Returns:
        str: A string containing the relevant policy information or guidelines.
    """

    rag = RAG()
    result = rag.query(question)

    return result