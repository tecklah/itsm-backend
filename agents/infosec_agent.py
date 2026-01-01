from util.file_util import load_config
from crewai import Agent
from tools.infosec_tools import retrieve_security_policy

def get_agent(llm) -> Agent:
    """Create infosec agent using YAML configuration."""
    config = load_config()
    
    return Agent(
        config=config['infosec_agent'],
        llm=llm,
        tools=[retrieve_security_policy],
    )

# def get_agent(llm) -> Agent:

#     return Agent(
#         role="Info Security Agent / infosec_agent",
#         goal=(
#             "Based on the user question or request, check whether there is any existing policy or guideline that addresses the user's question or request."
#             "If there is an existing policy or guideline, provide the relevant information."
#         ),
#         backstory=(
#             "You are the info security agent, an expert in cybersecurity policies and guidelines."
#             "Use the RAG approach to retrieve relevant policies or guidelines to answer user queries."
#             "DO NOT hallucinate if the results from the knowledge source do not contain relevant answer."
#             "If there is no relevant policy or guideline, inform the user accordingly."
#         ),
#         llm=llm,
#         function_calling_llm=None,  # Optional: Separate LLM for tool calling
#         verbose=True,  # Default: False
#         allow_delegation=False,  # Default: False
#         max_iter=10,  # Default: 20 iterations
#         max_rpm=None,  # Optional: Rate limit for API calls
#         max_execution_time=30,  # Optional: Maximum execution time in seconds
#         max_retry_limit=2,  # Default: 2 retries on error
#         allow_code_execution=False,  # Default: False
#         code_execution_mode="safe",  # Default: "safe" (options: "safe", "unsafe")
#         respect_context_window=True,  # Default: True
#         use_system_prompt=True,  # Default: True
#         multimodal=False,  # Default: False
#         inject_date=False,  # Default: False
#         date_format="%Y-%m-%d",  # Default: ISO format
#         reasoning=False,  # Default: False
#         max_reasoning_attempts=None,  # Default: None
#         tools=[retrieve_security_policy],  # Optional: List of tools
#         knowledge_sources=None,  # Optional: List of knowledge sources
#         embedder=None,  # Optional: Custom embedder configuration
#         system_template=None,  # Optional: Custom system prompt template
#         prompt_template=None,  # Optional: Custom prompt template
#         response_template=None,  # Optional: Custom response template
#         step_callback=None,  # Optional: Callback function for monitoring
#     )