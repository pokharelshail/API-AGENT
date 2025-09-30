from langchain.tools import tool
import requests
from pydantic import BaseModel, Field
from typing import Any, Optional, Dict


class APIResponse(BaseModel):
    """Pydantic model for API responses"""
    success: bool = Field(description="Whether the API request was successful")
    status_code: Optional[int] = Field(default=None, description="HTTP status code")
    data: Optional[Any] = Field(default=None, description="Response data from the API")
    error: Optional[str] = Field(default=None, description="Error message if request failed")
    url: str = Field(description="The URL that was requested")
    method: str = Field(description="HTTP method used (GET, POST, etc.)")
    
    class Config:
        json_encoders = {
            # Handle any special encoding if needed
        }


@tool
def get_api_request(url: str, headers: dict = None) -> APIResponse:
    """
    Make a GET request to the specified URL.
    
    Args:
        url: The API endpoint URL to fetch data from
        headers: Optional dictionary of HTTP headers to include in the request
        
    Returns:
        APIResponse: Structured response with success status, data, and metadata
    """
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        return APIResponse(
            success=True,
            status_code=response.status_code,
            data=response.json(),
            error=None,
            url=url,
            method="GET"
        )
    except requests.exceptions.RequestException as e:
        return APIResponse(
            success=False,
            status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
            data=None,
            error=str(e),
            url=url,
            method="GET"
        )


@tool
def post_api_request(url: str, data: dict, headers: dict = None) -> APIResponse:
    """
    Make a POST request to the specified URL with data.
    
    Args:
        url: The API endpoint URL
        data: Dictionary of data to send in the request body
        headers: Optional dictionary of HTTP headers to include in the request
        
    Returns:
        APIResponse: Structured response with success status, data, and metadata
    """
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        
        return APIResponse(
            success=True,
            status_code=response.status_code,
            data=response.json(),
            error=None,
            url=url,
            method="POST"
        )
    except requests.exceptions.RequestException as e:
        return APIResponse(
            success=False,
            status_code=getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
            data=None,
            error=str(e),
            url=url,
            method="POST"
        )