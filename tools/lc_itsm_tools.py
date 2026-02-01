from common.constants import FACILITY_RESET_PASSWORD_URL, FACILITY_SYSTEM_HEALTH_URL, FACILITY_GET_USER_BOOKING_URL
from langchain.tools import tool
from rag import RAG
import requests
import os
import json

def build_itsm_tools(llm, db_connection):
    """
    Factory that builds tools needing access to the shared LLM.
    """

    @tool(
        "create_service_request", 
        description="This is a tool to create a service request in the ITSM application.", 
        return_direct=False
    )
    def create_service_request(message: str, title: str, description: str, application: str, username: str) -> str:
        """
        This is a tool for ITSM application.
        The purpose of this tool is to create a service request in the ITSM application.
        
        Args:
            title (str): The title of the service request.
            description (str): The description of the service request.
            application (str): The application related to the service request.
            username (str): The username who is creating the service request.

        Returns:
            str: A string containing the status of the service request creation.
        """

        if db_connection is None:
            return "Error: Database connection not available"
        
        # Validate required fields
        if not title or not description or not application or not username:
            return "Error: All fields (title, description, application, username) are required"
        
        try:
            status = 'OPEN'
            
            cursor = db_connection.cursor()
            cursor.execute(
                "INSERT INTO service_request (title, description, application, username, status, date_created) VALUES (%s, %s, %s, %s, %s, NOW()) RETURNING id, title, description, application, status",
                (title, description, application, username, status)
            )
            
            record = cursor.fetchone()
            db_connection.commit()
            cursor.close()
            
            if record:
                return f"Service request created successfully. ID: {record[0]}, Title: {record[1]}, Status: {record[4]}"
            else:
                return "Error: Failed to create service request"
                
        except Exception as e:
            db_connection.rollback()
            return f"Error creating service request: {str(e)}"
    
    return [create_service_request]

