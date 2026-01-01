from crewai import Task

def get_retrieve_password_policy_task(agent) -> Task:
    
    return Task(
        description=(
            'Retrieve the password policy guidelines from the security knowledge base. '
            'The password policy should include requirements such as minimum length, '
            'character requirements (uppercase, lowercase, numbers, special characters), '
            'and any other relevant password creation rules.'
        ),
        expected_output=(
            'A detailed description of the password policy requirements that can be used '
            'to generate a compliant temporary password.'
        ),
        agent=agent,
    )

def get_retrieve_security_policy_task(agent) -> Task:
    return Task(
        description=(
            'Analyze the user question or request: [{question}]. '
            'Based on the question, retrieve the relevant information security policy or guidelines '
            'from the security knowledge base. This may include policies related to: '
            '- Password requirements and complexity rules '
            '- Access control and authentication '
            '- Network security '
            '- Data protection and encryption '
            '- Incident response procedures '
            '- Any other security-related policies relevant to the user\'s question. '
            'Provide comprehensive and accurate policy information that addresses the user\'s needs.'
        ),
        expected_output=(
            'A detailed description of the relevant security policy or guidelines that directly '
            'addresses the user\'s question. The output should be clear, complete, and ready to be '
            'used by other agents or provided to the user.'
        ),
        agent=agent,
    )