from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from tools.api_tool import get_api_request, post_api_request
from pydantic import BaseModel, Field
from typing import Any, Optional, List, Dict
from datetime import datetime

load_dotenv()


class SessionContext(BaseModel):
    """Pydantic model for session context"""
    user_input: str = Field(description="User's input message")
    agent_response: str = Field(description="Agent's response message")
    timestamp: datetime = Field(default_factory=datetime.now, description="When this exchange occurred")
    tools_used: Optional[List[str]] = Field(default=None, description="Tools used in this exchange")
    api_calls: Optional[List[Dict[str, Any]]] = Field(default=None, description="API calls made in this exchange")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionManager:
    """Manages conversation session without artificial limits"""
    
    def __init__(self, max_exchanges: int = 50):
        self.max_exchanges = max_exchanges  # Reasonable limit on number of exchanges, not characters
        self.conversation_history: List[SessionContext] = []
    
    def add_exchange(self, user_input: str, agent_response: str, tools_used: Optional[List[str]] = None, 
                     api_calls: Optional[List[Dict[str, Any]]] = None) -> None:
        """Add a new exchange to the session context"""
        exchange = SessionContext(
            user_input=user_input,
            agent_response=agent_response,
            tools_used=tools_used,
            api_calls=api_calls
        )
        
        self.conversation_history.append(exchange)
        
        # Only trim if we have too many exchanges (not based on character count)
        if len(self.conversation_history) > self.max_exchanges:
            self.conversation_history.pop(0)  # Remove oldest exchange
    
    def get_context_summary(self) -> str:
        """Get a summary of the conversation context (last 5 exchanges)"""
        if not self.conversation_history:
            return ""
        
        context_parts = []
        # Get last 5 exchanges for context
        recent_exchanges = self.conversation_history[-5:]
        for exchange in recent_exchanges:
            context_parts.append(f"User: {exchange.user_input}")
            context_parts.append(f"Agent: {exchange.agent_response}")
        
        return "\n".join(context_parts)
    
    def get_full_context(self) -> str:
        """Get the full conversation context"""
        if not self.conversation_history:
            return ""
        
        context_parts = []
        for exchange in self.conversation_history:
            context_parts.append(f"User: {exchange.user_input}")
            context_parts.append(f"Agent: {exchange.agent_response}")
        
        return "\n".join(context_parts)
    
    def clear_session(self) -> None:
        """Clear the session context"""
        self.conversation_history.clear()
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        total_chars = sum(len(exchange.user_input) + len(exchange.agent_response) 
                          for exchange in self.conversation_history)
        
        return {
            "exchanges_count": len(self.conversation_history),
            "total_characters": total_chars,
            "average_exchange_length": total_chars / len(self.conversation_history) if self.conversation_history else 0,
            "max_exchanges": self.max_exchanges
        }


class AgentResponse(BaseModel):
    """Pydantic model for agent responses"""
    success: bool = Field(description="Whether the agent processed the request successfully")
    message: str = Field(description="The main response message from the agent")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the response was generated")
    tools_used: Optional[List[str]] = Field(default=None, description="List of tools that were used during processing")
    api_calls: Optional[List[Dict[str, Any]]] = Field(default=None, description="Details of any API calls made")
    error: Optional[str] = Field(default=None, description="Error message if processing failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata about the response")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Agent:
    def __init__(self, max_exchanges: int = 50, verbose: bool = False):
        # Setup session manager with exchange limit, not character limit
        self.session_manager = SessionManager(max_exchanges)
        self.verbose = verbose
        # Setup LLM
        self.chat_model = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-001",
            temperature=0.1
        )
        
        # Setup tools
        self.tools = [
            get_api_request,
            post_api_request
        ]
        
        # Create system prompt
        system_prompt = """You are an intelligent API agent that can interact with web APIs.

Your capabilities:
- Make GET requests to retrieve data
- Make POST requests to send data
- Parse and analyze API responses
- Handle errors gracefully
- Remember conversation context from previous exchanges
- Reference previous API calls and their results

When working with APIs:
1. Validate URLs before making requests
2. Explain what you're doing
3. Present results in a structured format
4. Handle errors with helpful messages
5. Reference previous conversation context when relevant
6. Build upon previous API calls when appropriate

RESPONSE FORMATTING RULES:
- When making API calls, format your response as:
  📡 API Request: [METHOD] [URL]
  📋 Headers: [list headers if any]
  ✅ Status: [status code]
  📄 Response Data:
  [formatted JSON response]
  
- For errors, format as:
  ❌ Error: [error message]
  🔍 Details: [additional context]

- Keep responses concise but informative
- Always show the actual data received, not just confirmation messages
- Reference previous API calls or data when relevant
- Build upon previous results when making follow-up requests"""
        
        # Create prompt template with context
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Previous conversation context:\n{context}\n\nCurrent request: {input}"),
            ("placeholder", "{agent_scratchpad}")
        ])
        
        # Create agent
        agent = create_tool_calling_agent(self.chat_model, self.tools, prompt)
        
        # Create executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.verbose,
            max_iterations=10
        )
        
        print("✅ Agent ready with Gemini 2.0 Flash")
        print(f"📝 Session management: Up to {max_exchanges} exchanges (no character limits)")
        if verbose:
            print("🔍 Verbose mode: ON (detailed debugging enabled)")
    
    def run(self, input_text: str) -> AgentResponse:
        """Run the agent with user input and session context"""
        tools_used = []
        api_calls = []
        
        try:
            # Get conversation context
            context = self.session_manager.get_context_summary()
            
            # Prepare input with context
            input_with_context = {
                "input": input_text,
                "context": context
            }
            
            result = self.agent_executor.invoke(input_with_context)
            
            # Extract tool usage information from the result
            if "intermediate_steps" in result:
                for step in result["intermediate_steps"]:
                    if len(step) >= 2:
                        tool_name = step[0].tool if hasattr(step[0], 'tool') else str(step[0])
                        tools_used.append(tool_name)
                        
                        # If it's an API call, capture the details
                        if hasattr(step[1], 'success') and hasattr(step[1], 'url'):
                            api_calls.append({
                                "tool": tool_name,
                                "url": step[1].url,
                                "method": step[1].method,
                                "success": step[1].success,
                                "status_code": step[1].status_code
                            })
            
            # Add this exchange to session context
            self.session_manager.add_exchange(
                user_input=input_text,
                agent_response=result["output"],
                tools_used=tools_used,
                api_calls=api_calls
            )
            
            return AgentResponse(
                success=True,
                message=result["output"],
                tools_used=tools_used if tools_used else None,
                api_calls=api_calls if api_calls else None,
                metadata={
                    "input": input_text, 
                    "model": "gemini-2.0-flash-001",
                    "context_exchanges": len(self.session_manager.conversation_history)
                }
            )
            
        except Exception as e:
            return AgentResponse(
                success=False,
                message="An error occurred while processing your request",
                error=str(e),
                tools_used=tools_used if tools_used else None,
                api_calls=api_calls if api_calls else None,
                metadata={
                    "input": input_text, 
                    "model": "gemini-2.0-flash-001",
                    "context_exchanges": len(self.session_manager.conversation_history)
                }
            )
    
    def clear_session(self) -> None:
        """Clear the current session context"""
        self.session_manager.clear_session()
        print("🧹 Session context cleared")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get information about the current session"""
        stats = self.session_manager.get_session_stats()
        return {
            "exchanges_count": stats["exchanges_count"],
            "total_characters": stats["total_characters"],
            "average_exchange_length": stats["average_exchange_length"],
            "max_exchanges": stats["max_exchanges"],
            "context_usage_percent": (stats["exchanges_count"] / stats["max_exchanges"]) * 100
        }