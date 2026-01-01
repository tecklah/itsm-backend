from crewai import Task

def get_supervise_task(agent) -> Task:
    
    return Task(
        # description=(
        #     'Analyse the question [{question}] and decide which agent is best suited to handle it.'
        # ),
        description=(
            'Handle the user question: [{question}]. '
            'You MUST delegate the necessary work to the Facility Application Agent and Info Security Agent to resolve the request. '
            '1. Ask the Info Security Agent to retrieve the relevant security policies (especially password complexity). '
            '2. Based on the policy, ask the Facility Application Agent to reset the password with a compliant temporary password. '
            'Ensure the final result confirms the action taken.'
        ),
        expected_output=(
            'Return a dictionary indicating the status of the task completion and a message of the action taken.'
            '{"status": "success" | "failure", "message": str}'
        ),
        agent=agent,
    )
