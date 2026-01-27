import os
from pinecone import Pinecone

class RAG:
    """
    RAG(Retrieval-Augmented Generation) class built upon OpenAI and Milvus.
    """

    def __init__(
        self,
        model,
        api_key: str = os.getenv("PINECONE_API_KEY"),
        host: str = os.getenv("PINECONE_HOST"),
        index_name: str = os.getenv("PINECONE_INDEX_NAME"),
    ):
        self.model = model
        self.pinecone = Pinecone(api_key=api_key)
        self.host = host
        self.index_name = index_name
        self.index = self.pinecone.Index(host=host, index_name=index_name)

    def retrieve(
        self, 
        question: str,
        top_k: int=5,
        top_n: int=3,
        namespace="__default__"
    ):
        results = self.index.search(
            namespace=namespace, 
            query={
                "inputs": {"text": question}, 
                "top_k": top_k
            },
            fields=["category", "text"],
            rerank={
                "model": "bge-reranker-v2-m3",
                "top_n": top_n,
                "rank_fields": ["text"]
            }
        )

        text_array = [hit['fields']['text'] for hit in results['result']['hits']]

        return text_array
    
    def query(
        self,
        question: str,
        top_k: int=5,
        top_n: int=3,
        namespace="__default__"
    ):
        print("*** RAG Query:", question)
        
        results = self.index.search(
            namespace=namespace, 
            query={
                "inputs": {"text": question}, 
                "top_k": top_k
            },
            fields=["category", "text"],
            rerank={
                "model": "bge-reranker-v2-m3",
                "top_n": top_n,
                "rank_fields": ["text"]
            }
        )

        text_array = [hit['fields']['text'] for hit in results['result']['hits']]
        concatenated_text = "\n".join(text_array)

        prompt = (
            "You are an assistant that answers questions about the Facility Application "
            "based ONLY on the provided context.\n\n"
            "Context:\n{context}\n\n"
            "Question:\n{question}\n\n"
            "Use the context above to answer the question, even if it is only partially relevant."
            "Keep your answer concise and to the point. DO NOT fabricate any information. "
            "Reply 'No relevant information available.' if the context is absolutely not related to the question."
        ).format(context=concatenated_text, question=question)

        response = self.model.invoke(prompt)

        print("*** RAG Response:\n", response.content)

        return response.content, text_array
    
