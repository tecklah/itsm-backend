from crewai import Agent
from tools.facility_tools import reset_user_password
from util.file_util import load_config

def get_agent(llm) -> Agent:
    """Create facility agent using YAML configuration."""
    config = load_config()
    
    return Agent(
        config=config['facility_agent'],
        llm=llm,
        tools=[reset_user_password],
    )

# def get_agent(llm) -> Agent:

#     return Agent(
#         role="Facility Application Agent / facility_agent",
#         goal=(
#             "You are the agent that handles user questions or requests related to the Facility application. "
#             "Based on the user question or request, use the available tools to assist the user effectively."
#             "Type of requests that you can handle:"
#             "1. Resetting user passwords."
#         ),
#         backstory=(
#             "The Facility application is an online application that allows user to book facilities and manage their bookings."
#             "You have access to tools that can help users reset their passwords and manage their bookings."
#         ),
#         llm=llm,
#         function_calling_llm=None,  # Optional: Separate LLM for tool calling
#         verbose=True,  # Default: False
#         allow_delegation=True,  # Enable delegation to infosec agent for policy retrieval
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
#         tools=[reset_user_password],  # Optional: List of tools
#         knowledge_sources=None,  # Optional: List of knowledge sources
#         embedder=None,  # Optional: Custom embedder configuration
#         system_template=None,  # Optional: Custom system prompt template
#         prompt_template=None,  # Optional: Custom prompt template
#         response_template=None,  # Optional: Custom response template
#         step_callback=None,  # Optional: Callback function for monitoring
#     )