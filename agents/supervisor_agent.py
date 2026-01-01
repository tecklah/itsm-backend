from util.file_util import load_config
from crewai import Agent

def get_agent(llm) -> Agent:
    """Create supervisor agent using YAML configuration."""
    config = load_config()
    
    return Agent(
        config=config['supervisor_agent'],
        llm=llm,
        tools=[],
    )

# def get_agent(llm) -> Agent:

#     return Agent(
#         role="Supervisor Agent",
#         # goal="Based on the user question or request, decide whether you have a task that can answer the user's question or request directly, or whether you need to delegate the task to another specialized agent.",
#         # backstory=(
#         #     "You are the main or supervisor agent that manage or route the user's question or request to the most suitable task or agent."
#         #     "If you are not able to find a suitable task or agent, you should inform the user accordingly."
#         #     "DO NOT hallucinate if there are any tasks or agents that do not exist."
#         # ),
#         goal='Efficiently manage the crew and ensure high-quality task completion. Coordinate and delegate tasks to appropriate specialized agents based on the type of request.',
#         backstory="""You are a supervisor coordinating a team of specialized agents. 
#         Your job is to analyze incoming requests and delegate them to the appropriate agent:
#         - infosec_agent: for security policies, password policies, and security-related queries
#         - facility_agent: for password resets, user management, and facility system operations
        
#         You MUST delegate tasks to the appropriate agents. Do not attempt to execute tasks directly.""",
#         llm=llm,
#         function_calling_llm=None,  # Optional: Separate LLM for tool calling
#         verbose=True,  # Default: False
#         allow_delegation=True,  # Enable delegation to other agents
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
#         tools=[],  # Optional: List of tools
#         knowledge_sources=None,  # Optional: List of knowledge sources
#         embedder=None,  # Optional: Custom embedder configuration
#         system_template=None,  # Optional: Custom system prompt template
#         prompt_template=None,  # Optional: Custom prompt template
#         response_template=None,  # Optional: Custom response template
#         step_callback=None,  # Optional: Callback function for monitoring
#     )