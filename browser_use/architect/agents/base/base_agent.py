from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, Union

from browser_use.architect.memory.memory_manager import log_message
from browser_use.architect.tools.llm_interface import _run_llm_with_retry

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the Architect system.
    
    This class defines the core interface and shared functionality that all agents must implement.
    It provides:
    - Standard initialization with goal and model
    - Abstract run method that must be implemented by subclasses
    - Utility methods for LLM interaction and logging
    - Standardized response format
    """
    
    def __init__(self, name: str, goal: str, model: str = "gemini-2.0-flash-lite"):
        """
        Initialize a base agent.
        
        Args:
            name: The name of the agent
            goal: The goal or task to accomplish
            model: The LLM model to use (default: gemini-2.0-flash-lite)
        """
        self.name = name
        self.goal = goal
        self.model = model
        
    @abstractmethod
    async def run(self, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Execute the agent's main task.
        
        Args:
            callback: Optional callback function for progress updates
            
        Returns:
            A dictionary containing at least:
            {
                "status": "success" | "error",
                "data": Any  # The actual result data
                "error"?: str  # Error message if status is "error"
            }
        """
        pass
        
    async def _run_llm(self, prompt: str) -> Dict[str, Any]:
        """
        Run the LLM with error handling and standardized output.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Standardized response dictionary
        """
        try:
            result = await _run_llm_with_retry(prompt, self.model)
            
            # Handle different response types
            if isinstance(result, dict):
                return {
                    "status": "success",
                    "data": result
                }
            elif isinstance(result, str):
                return {
                    "status": "success",
                    "data": result
                }
            else:
                return {
                    "status": "success",
                    "data": str(result)
                }
                
        except Exception as e:
            log_message(self.name, f"❌ LLM error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "data": None
            }
            
    def log(self, message: str) -> None:
        """
        Log a message with the agent's name.
        
        Args:
            message: The message to log
        """
        log_message(self.name, message)
        
    async def _handle_callback(self, 
                             callback: Optional[Callable], 
                             status: str, 
                             data: Dict[str, Any]) -> None:
        """
        Handle callback if provided.
        
        Args:
            callback: The callback function
            status: Status type
            data: Data to pass to callback
        """
        if callback:
            await callback(status, {
                "agent": self.name,
                **data
            }) 