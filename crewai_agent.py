from crewai import Agent, Task, Crew, Process, LLM
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from agents import facility_agent, supervisor_agent, infosec_agent
from tools import facility_tools, infosec_tools
from tasks import facility_tasks, supervisor_tasks, infosec_tasks
load_dotenv()

llm = ChatOpenAI(
    openai_api_base="https://api.openai.com/v1",
    openai_api_key=os.getenv('OPENAI_API_KEY'),
    model_name="gpt-4.1",
    temperature=0.1,
    max_tokens=1000,
    # max_completion_tokens=1000,
)

supervisor_agent = supervisor_agent.get_agent(llm)
facility_agent = facility_agent.get_agent(llm)
infosec_agent = infosec_agent.get_agent(llm)

get_retrieve_security_policy_task = infosec_tasks.get_retrieve_security_policy_task(infosec_agent)
reset_password_task = facility_tasks.get_reset_password_task(facility_agent)
reset_password_task.context = [get_retrieve_security_policy_task]  # Use policy task output as context
supervise_task = supervisor_tasks.get_supervise_task(supervisor_agent)

crew = Crew(
    agents=[facility_agent, infosec_agent],
    tasks=[supervise_task],
    verbose=True,
    process=Process.sequential,
    # process=Process.hierarchical,
    # planning=True,
    manager_agent=supervisor_agent,
    # manager_llm=LLM(model="gpt-4.1", temperature=0.1, max_tokens=1000),
)

result = crew.kickoff(inputs={'question': 'Please help me reset my password as I have forgotten it. My user account on Facility system is user1.'})
print("Final Result:")
print(result)

print(crew.usage_metrics)