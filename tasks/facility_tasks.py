from crewai import Task
from tools import facility_tools

def get_reset_password_task(agent) -> Task:
    
    return Task(
        description=(
            'This task is to reset user password in Facility application. '
            'Analyse the question [{question}] and perform the reset if necessary. '
            'DO NOT accept the password key from the user directly. '
            'Use the password policy information from the context provided by previous tasks. '
            'Based on the policies, generate a compliant temporary password and use it to reset the user password.'
        ),
        expected_output=(
            'Return a dictionary indicating the status of the password reset operation and a message of the action taken including the temporary password generated. '
            '{"status": "success" | "failure", "message": str}'
        ),
        agent=agent,
        # tools=[facility_tools.reset_user_password],
        context=[]
)