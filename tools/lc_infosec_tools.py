import os
from rag import RAG
from langchain.tools import tool

def build_infosec_tools(llm):
    """
    Factory that builds tools for infosec sub-agent.
    """

    @tool("retrieve_security_policy", description="Retrieve InfoSecurity policies from RAG based on a question", return_direct=False)
    def retrieve_security_policy(question: str) -> str:
        """
        This is a tool for querying against the InfoSecurity policy.
        The purpose of this tool is to retrieve any related policies or guidelines based on the user's question.
        
        Args:
            question (str): The user's question or request related to InfoSecurity policies.

        Returns:
            str: A string containing the relevant policy information or guidelines.
        """

        rag = RAG(
            model=llm,
            api_key=os.getenv("PINECONE_API_KEY"),
            host=os.getenv("PINECONE_HOST_INFOSEC_POLICY"),
            index_name=os.getenv("PINECONE_INDEX_NAME_INFOSEC_POLICY")
        )
        
        result, contexts = rag.query(question, top_k=3, top_n=2)

        print("*** InfoSecurity Policy Retrieval Result:")
        print(result)

        return result
    
    return [retrieve_security_policy]