import os
import uuid
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from langgraph.types import Command
from tools.lc_facility_tools import build_facility_tools
from tools.lc_infosec_tools import build_infosec_tools
from tools.lc_itsm_tools import build_itsm_tools
from util.log_util import print_trace, print_message
from util.db_util import get_langchain_db_connection, get_db_connection
from prompts.agent_prompts import SUPERVISOR_AGENT_PROMPT, ITSM_DATABASE_AGENT_PROMPT, INFO_SECURITY_AGENT_PROMPT, FACILITY_APPLICATION_AGENT_PROMPT, ITSM_APPLICATION_AGENT_PROMPT
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langgraph.checkpoint.memory import MemorySaver
from pprint import pprint

load_dotenv()

llm = ChatOpenAI(
    base_url="https://api.openai.com/v1",
    api_key=os.getenv('OPENAI_API_KEY'),
    model="gpt-5.1",
    temperature=0.1,
    max_tokens=1000,
)

db_connection = get_db_connection(os.getenv('DB_NAME'), os.getenv('DB_USERNAME'), os.getenv('DB_PASSWORD'), os.getenv('DB_HOST'), os.getenv('DB_PORT'))
langchain_db_connection = get_langchain_db_connection(os.getenv('DB_NAME'), os.getenv('DB_USERNAME'), os.getenv('DB_PASSWORD'), os.getenv('DB_HOST'))
sql_database_toolkit = SQLDatabaseToolkit(db=langchain_db_connection, llm=llm)
sql_database_tools = sql_database_toolkit.get_tools()

itsm_database_subagent = {
    "name": "itsm-database-agent",
    "description": "Used to interact with the ITSM application database for querying and updating incident tickets and service requests.",
    "system_prompt": ITSM_DATABASE_AGENT_PROMPT.format(
        dialect=langchain_db_connection.dialect,
        top_k=3,
    ),
    "tools": sql_database_tools,
}

itsm_application_subagent = {
    "name": "itsm-application-agent",
    "description": "Used to handle tasks related to the ITSM application, such as creating service requests. Or, just answer user questions generally.",
    "system_prompt": ITSM_APPLICATION_AGENT_PROMPT,
    "tools": build_itsm_tools(llm, db_connection),
    "interrupt_on": {
        "create_service_request": { "allowed_decisions": ["approve", "reject"] }
    }
}

facility_application_subagent = {
    "name": "facility-application-agent",
    "description": "Used to handle tasks related to the Facility application, such as user management, password resets, and system health checks.",
    "system_prompt": FACILITY_APPLICATION_AGENT_PROMPT,
    "tools": build_facility_tools(llm),
    "interrupt_on": {
        "reset_user_password": { "allowed_decisions": ["approve", "reject"] },
        "seek_approval": { "allowed_decisions": ["approve", "reject"] },
    }
}

info_security_subagent = {
    "name": "info-security-agent",
    "description": "Used to handle tasks related to InfoSecurity policies and guidelines.",
    "system_prompt": INFO_SECURITY_AGENT_PROMPT,
    "tools": build_infosec_tools(llm),
}

subagents = [info_security_subagent, facility_application_subagent, itsm_database_subagent, itsm_application_subagent]

agent = create_deep_agent(
    model=llm,
    system_prompt=SUPERVISOR_AGENT_PROMPT,
    subagents=subagents,
    checkpointer = MemorySaver()
)

def make_decision(session_id, decision):
    print(f"Session ID: {session_id}")
    config = {"configurable": {"thread_id": session_id}}

    decision_obj = {"type": decision.lower()}
    last_message = None
    
    for chunk in agent.stream(
        Command(resume={"decisions": [decision_obj]}),
        config=config,
        stream_mode="values",
    ):
  
        # Check for subsequent interrupts after decision
        if "__interrupt__" in chunk:
            print("======== INTERRUPT DETECTED ========")
            print(chunk)
            print("=====================================")
            interrupt_data = chunk["__interrupt__"]
            if isinstance(interrupt_data, tuple) and len(interrupt_data) > 0:
                interrupt = interrupt_data[0]
                if hasattr(interrupt, 'value'):
                    interrupt_value = interrupt.value
                    action_requests = interrupt_value.get('action_requests', [])
                    review_configs = interrupt_value.get('review_configs', [])
                    
                    if action_requests and review_configs:
                        action_request = action_requests[0]
                        review_config = review_configs[0]
                        
                        # Return subsequent interrupt information
                        return {
                            'type': 'interrupt',
                            'action_name': action_request.get('name'),
                            'args': action_request.get('args'),
                            'description': action_request.get('description'),
                            'allowed_decisions': review_config.get('allowed_decisions', []),
                            'session_id': session_id
                        }
        
        if "messages" in chunk:
            last_message = chunk["messages"][-1]
            print_message(last_message, db_connection)

    return {
        'type': 'message',
        'message': last_message.content if last_message else None
    }

def run(question, session_id=None, disable_interrupts=False, is_test=False):
    print(f"Session ID: {session_id}")
    last_message = None

    # Configure thread_id for memory and human-in-the-loop
    config = {"configurable": {"thread_id": session_id or str(uuid.uuid4())}}
        
    messages = []
    if is_test:
        messages.append({
            "role": "system",
            "content": "You are running in test mode. You should still go through all the necessary steps to fulfill the request but do NOT update the database."
        })
    
    messages.append({
        "role": "user",
        "content": question,
    })

    for chunk in agent.stream(
        {"messages": messages},
        config=config,
        stream_mode="values",
    ):
        
        # Check for human-in-the-loop interrupt
        if "__interrupt__" in chunk:
            print("======== INTERRUPT DETECTED ========")
            print(chunk)
            print("=====================================")

            # Auto-approve if interrupts disabled
            # if disable_interrupts or is_test:
            #     print(">>>>>>>> Auto-approving interrupt...")
            #     agent.invoke(
            #         Command(resume={"decisions": [{"type": "approve"}]}),
            #         config=config
            #     )
            #     continue

            interrupt_data = chunk["__interrupt__"]
            if isinstance(interrupt_data, tuple) and len(interrupt_data) > 0:
                interrupt = interrupt_data[0]
                if hasattr(interrupt, 'value'):
                    interrupt_value = interrupt.value
                    action_requests = interrupt_value.get('action_requests', [])
                    review_configs = interrupt_value.get('review_configs', [])
                    
                    if action_requests and review_configs:
                        action_request = action_requests[0]
                        review_config = review_configs[0]
                        
                        # Return interrupt information to frontend
                        return {
                            'type': 'interrupt',
                            'action_name': action_request.get('name'),
                            'args': action_request.get('args'),
                            'description': action_request.get('description'),
                            'allowed_decisions': review_config.get('allowed_decisions', []),
                            'session_id': session_id or str(uuid.uuid4())
                        }
        
        if "messages" in chunk:
            last_message = chunk["messages"][-1]
            print_message(last_message, db_connection)

    return {
        'type': 'message',
        'message': last_message.content
    }        

if __name__ == "__main__":
    # run("Reset the password for privileged user john@example.com in Facility application.")
    run("""
        A new ITSM incident ticket has been created with the following details:
        Title: Cannot access exam result system
        Description: I am not able to access exam result system. My account is user2.
    """)  