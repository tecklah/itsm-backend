import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool
from tools.lc_facility_tools import reset_user_password
from tools.lc_infosec_tools import retrieve_security_policy
from util.log_util import print_trace, print_message
from util.db_util import get_langchain_db_connection
from prompts.agent_prompts import SUPERVISOR_AGENT_PROMPT, INFO_SECURITY_AGENT_PROMPT, FACILITY_APPLICATION_AGENT_PROMPT, DATABASE_AGENT_PROMPT
from langchain_community.agent_toolkits import SQLDatabaseToolkit

load_dotenv()

llm = ChatOpenAI(
    base_url="https://api.openai.com/v1",
    api_key=os.getenv('OPENAI_API_KEY'),
    model="gpt-5.1",
    temperature=0.1,
    max_tokens=1000,
)

langchain_db_connection = get_langchain_db_connection(os.getenv('DB_NAME'), os.getenv('DB_USERNAME'), os.getenv('DB_PASSWORD'), os.getenv('DB_HOST'))
sql_database_toolkit = SQLDatabaseToolkit(db=langchain_db_connection, llm=llm)
sql_database_tools = sql_database_toolkit.get_tools()

# runtime_context = {"db_connection": langchain_db_connection, "tools": sql_database_tools}

# itsm_db_agent = create_agent(
#     model=llm,
#     tools=sql_database_tools,
#     system_prompt=DATABASE_AGENT_PROMPT.format(
#         dialect=langchain_db_connection.dialect,
#         top_k=1,
#     )
# )

info_security_agent = create_agent(
    model=llm,
    tools=[retrieve_security_policy],
    system_prompt=INFO_SECURITY_AGENT_PROMPT,
)

facility_application_agent = create_agent(
    model=llm,
    tools=[reset_user_password],
    system_prompt=FACILITY_APPLICATION_AGENT_PROMPT,
)

@tool("info-security-agent", description="Agent to handle InfoSecurity related tasks.")
def get_info_security_agent(request: str) -> str:
    return info_security_agent.invoke({
        "messages": [{"role": "user", "content": request}]
    })

@tool("facility-application-agent", description="Agent to handle Facility application related tasks.")
def get_facility_application_agent(request: str) -> str:
    return facility_application_agent.invoke({
        "messages": [{"role": "user", "content": request}]
    })

SUPERVISOR_PROMPT = """
    IMPORTANT: sub-agent is also referring to tool.
    {supervisor_agent_prompt}
""".format(supervisor_agent_prompt=SUPERVISOR_AGENT_PROMPT)

supervisor_agent = create_agent(
    model=llm,
    tools=[get_info_security_agent, get_facility_application_agent],
    system_prompt=SUPERVISOR_PROMPT,
)

# result = supervisor_agent.invoke({
#     "messages": [{"role": "user", "content": "Reset the password for privileged user user1 in Facility application."}]
# })

async def run():
    async for chunk in supervisor_agent.astream(
        {"messages": [{"role": "user", "content": "Reset the password for privileged user john@example.com in Facility application."}]},
        stream_mode="values",
    ):
        if "messages" in chunk:
            last = chunk["messages"][-1]
            print_message(last)
            # This prints "Human", "AI", or "Tool" with role and content
            # last.pretty_print()

asyncio.run(run())