import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from deepagents import create_deep_agent
from tools.lc_facility_tools import build_facility_tools
from tools.lc_infosec_tools import build_infosec_tools
from util.log_util import print_trace, print_message
from util.db_util import get_langchain_db_connection, get_db_connection
from prompts.agent_prompts import SUPERVISOR_AGENT_PROMPT, ITSM_DATABASE_AGENT_PROMPT, INFO_SECURITY_AGENT_PROMPT, FACILITY_APPLICATION_AGENT_PROMPT
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from pprint import pprint

load_dotenv()

llm = ChatOpenAI(
    base_url="https://api.openai.com/v1",
    api_key=os.getenv('OPENAI_API_KEY'),
    model="gpt-5.1",
    temperature=0.1,
    max_tokens=10000,
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

facility_application_subagent = {
    "name": "facility-application-agent",
    "description": "Used to handle tasks related to the Facility application, such as user management, password resets, and system health checks.",
    "system_prompt": FACILITY_APPLICATION_AGENT_PROMPT,
    "tools": build_facility_tools(llm),
}

info_security_subagent = {
    "name": "info-security-agent",
    "description": "Used to handle tasks related to InfoSecurity policies and guidelines.",
    "system_prompt": INFO_SECURITY_AGENT_PROMPT,
    "tools": build_infosec_tools(llm),
}

subagents = [info_security_subagent, facility_application_subagent, itsm_database_subagent]

agent = create_deep_agent(
    model=llm,
    system_prompt=SUPERVISOR_AGENT_PROMPT,
    subagents=subagents
)

def run(question, is_test=False):
    last_message = None

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
        stream_mode="values",
    ):
        if "messages" in chunk:
            last_message = chunk["messages"][-1]
            print_message(last_message, db_connection)

    return last_message

if __name__ == "__main__":
    # run("Reset the password for privileged user john@example.com in Facility application.")
    run("""
        A new ITSM incident ticket has been created with the following details:
        Title: Cannot access exam result system
        Description: I am not able to access exam result system. My account is user2.
    """)  