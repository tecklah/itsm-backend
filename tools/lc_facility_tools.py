from common.constants import FACILITY_RESET_PASSWORD_URL, FACILITY_SYSTEM_HEALTH_URL, FACILITY_GET_USER_BOOKING_URL
from langchain.tools import tool
from rag import RAG
import requests
import os
import json

@tool(
    "reset_user_password", 
    description="Reset a user's password in the Facility application", 
    return_direct=False
)
def reset_user_password(username: str, password: str) -> str:
    """
    This is a tool for Facility application.
    The purpose of this tool is to reset a user's password in the Facility application.
    Resets the password for the given username and return the status as a string.
    The username is not case-sensitive, convert it to lowercase before processing.
    
    Args:
        username (str): The username whose password needs to be reset.
        password (str): The new password to set for the user.

    Returns:
        str: A string containing the status of the password reset operation.
    """

    try:
        url = FACILITY_RESET_PASSWORD_URL
        payload = {
            "username": username.lower(),
            "new_password": password
        }
        
        response = requests.put(url, json=payload)        
        result = response.json()
        
        if result.get('status') == 'success':
            return f"Password for username: [{username}] has been reset successfully. {result.get('message', '')}"
        else:
            return f"Failed to reset password for username: [{username}]. {result.get('message', 'Unknown error')}"
    
    except requests.exceptions.RequestException as e:
        return f"Failed to reset password for username: [{username}]. Error: {str(e)}"


@tool(
    "get_user_booking", 
    description="Given a username, get a list of user bookings in the Facility application", 
    return_direct=False
)
def get_user_booking(username: str) -> str:
    """
    This is a tool for Facility application.
    The purpose of this tool is to get a list of user bookings in the Facility application.
    Retrieves the bookings for the given username and return the list as a formatted string.
    The username is not case-sensitive, convert it to lowercase before processing.
    
    Args:
        username (str): The username whose bookings need to be retrieved.

    Returns:
        str: A string containing the list of bookings or error message.
    """

    try:
        url = f"{FACILITY_GET_USER_BOOKING_URL}?username={username.lower()}"
        
        response = requests.get(url)        
        result = response.json()
        
        if result.get('status') == 'success':
            bookings = result.get('bookings', [])
            
            if not bookings:
                return f"No bookings found for username: [{username}]"
            
            return json.dumps({
                "username": username,
                "total_bookings": len(bookings),
                "bookings": bookings
            }, indent=2)
        else:
            return f"Failed to retrieve bookings for username: [{username}]. {result.get('message', 'Unknown error')}"
    
    except requests.exceptions.RequestException as e:
        return f"Failed to retrieve bookings for username: [{username}]. Error: {str(e)}"
    
@tool(
    "check_system_health", 
    description="Check the system health of the Facility application", 
    return_direct=False
)
def check_system_health() -> str:
    """
    The purpose of this tool is to check the system health (eg. application, database) of the Facility application.
    It will call the Facility system health endpoint. If the status is successful, it indicates that the application and
    database are healthy and will return the minutes since the latest booking. Else, it will return the failure message.  

    Args:

    Returns:
        str: A string containing the status of the system health check operation and also the latest booking date if status is successful.
    """

    try:
        url = FACILITY_SYSTEM_HEALTH_URL
        
        response = requests.get(url)        
        result = response.json()
        
        if result.get('status') == 'success':
            return f"System health check successful. Minutes since last booking: {result.get('minutes_since_last_booking', 'Not available')}"
        else:
            return f"System health check failed. Message: {result.get('message', 'Unknown error')}"
    
    except requests.exceptions.RequestException as e:
        return f"System health check failed. Error: {str(e)}"

def build_facility_tools(llm):
    """
    Factory that builds tools needing access to the shared LLM.
    """

    rag = RAG(
        model=llm,
        api_key=os.getenv("PINECONE_API_KEY"),
        host=os.getenv("PINECONE_HOST_FACILITY_GUIDE"),
        index_name=os.getenv("PINECONE_INDEX_NAME_FACILITY_GUIDE")
    )
    
    @tool(
        "retrieve_troubleshooting_guide", 
        description="Retrieve Facility application troubleshooting guide from RAG based on a question", 
        return_direct=False
    )
    def retrieve_troubleshooting_guide(question: str) -> str:
        """
        This is a tool for getting the Facility application troubleshooting guide.
        The purpose of this tool is to retrieve any related troubleshooting information or guidelines based on the system or user issues.
        DO NOT provide any general or remediation information.

        Args:
            question (str): A concise description of the system or user issues related to Facility application.
        Returns:
            str: A string containing the relevant troubleshooting information or guidelines.
        """

        result, contexts = rag.query(question, top_k=5, top_n=3)

        print("*** Facility Troubleshooting Guide Retrieval Result:")
        print(result)

        return result
    
    return [reset_user_password, get_user_booking, check_system_health, retrieve_troubleshooting_guide]