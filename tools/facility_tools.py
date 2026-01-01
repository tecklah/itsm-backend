from crewai.tools import tool

@tool("reset_user_password")
def reset_user_password(username: str, password: str) -> dict:
    """
    This is a tool for Facility application.
    The purpose of this tool is to reset a user's password in the Facility application.
    Resets the password for the given username and return the status in as a dictionary.
    The username is not case-sensitive, convert it to lowercase before processing.
    
    Args:
        username (str): The username whose password needs to be reset.
        password (str): The new password to set for the user.

    Returns:
        dict: A dictionary containing the status of the password reset operation.
        {
            "status": "success" | "failure",
            "message": f"Password for user {username} has been reset."
        }
    """
    result = {
        "status": "success", 
        "message": f"Password for user {username} has been reset."
    }

    return result

