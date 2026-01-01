from deepeval.tracing import observe, update_current_span
from deepeval.test_case import LLMTestCase
from deepeval.dataset import EvaluationDataset, Golden
from deepeval.metrics import ContextualRelevancyMetric
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
import sys

# Load environment variables first
load_dotenv(dotenv_path='../.env')

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag import RAG

contextual_relevancy = ContextualRelevancyMetric(threshold=0.6, model="gpt-4.1-mini")

llm = ChatOpenAI(
    base_url="https://api.openai.com/v1",
    api_key=os.getenv('OPENAI_API_KEY'),
    model="gpt-4.1-mini",
    temperature=0.1,
    max_tokens=1000,
)

def test_infosecurity_retriever():

    rag = RAG(
        model=llm,
        api_key=os.getenv("PINECONE_API_KEY"),
        host=os.getenv("PINECONE_HOST_INFOSEC_POLICY"),
        index_name=os.getenv("PINECONE_INDEX_NAME_INFOSEC_POLICY")
    )

    @observe(metrics=[contextual_relevancy])
    def infosecurity_retriever(query):
        contexts = rag.retrieve(question=query, top_k=3, top_n=2)
        print("Retrieved lenContexts:", len(contexts))
        for i, ctx in enumerate(contexts, start=1):
            print(f"\n--- Context {i} ---")
            print(ctx)
        update_current_span(
            test_case=LLMTestCase(input=query, retrieval_context=contexts)
        )

    dataset = EvaluationDataset(
                goldens=[
                    Golden(input='What is the password policy for the organization?'),
                ])

    for golden in dataset.evals_iterator():
        infosecurity_retriever(golden.input)

def test_facility_application_retriever():

    rag = RAG(
        model=llm,
        api_key=os.getenv("PINECONE_API_KEY"),
        host=os.getenv("PINECONE_HOST_FACILITY_GUIDE"),
        index_name=os.getenv("PINECONE_INDEX_NAME_FACILITY_GUIDE")
    )

    @observe(metrics=[contextual_relevancy])
    def facility_application_retriever(query):
        contexts = rag.retrieve(question=query, top_k=5, top_n=3)
        print("Retrieved lenContexts:", len(contexts))
        for i, ctx in enumerate(contexts, start=1):
            print(f"\n--- Context {i} ---")
            print(ctx)
        update_current_span(
            test_case=LLMTestCase(input=query, retrieval_context=contexts)
        )

    dataset = EvaluationDataset(
                goldens=[
                    Golden(input='User made a booking but an error occurred. I need help resolving this issue.'),
                ])

    for golden in dataset.evals_iterator():
        facility_application_retriever(golden.input)

if __name__ == "__main__":
    #test_infosecurity_retriever()
    test_facility_application_retriever()
    sys.exit(0)


