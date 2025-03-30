"""
Template for dynamically generated agents.
This template provides a basic structure that all generated agents should follow.
"""

from typing import Dict, Any, Optional, Callable
from browser_use.architect.agents.base.base_agent import BaseAgent
from browser_use.architect.memory.memory_manager import log_message

class {agent_name}(BaseAgent):
    """
    {agent_description}
    """
    
    def __init__(self, name: str, goal: str, model: str = "gemini-2.0-flash-lite"):
        """Initialize the agent with the given goal."""
        super().__init__(name, goal, model)
        
    async def run(self, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Execute the agent's main task.
        
        Args:
            callback: Optional callback for progress updates
            
        Returns:
            Dictionary containing the execution results
        """
        self.log(f"🎯 Starting task: {self.goal}")
        
        try:
            # Report start
            if callback:
                await self._handle_callback(callback, "start", {
                    "goal": self.goal
                })
                
            # Main task implementation
            {task_implementation}
            
            # Process results
            result = {
                "status": "success",
                "data": response
            }
            
            # Report completion
            if callback:
                await self._handle_callback(callback, "complete", {
                    "result": result
                })
                
            return result
            
        except Exception as e:
            error_msg = f"Task failed: {str(e)}"
            self.log(f"❌ {error_msg}")
            
            if callback:
                await self._handle_callback(callback, "error", {
                    "error": error_msg
                })
                
            return {
                "status": "error",
                "error": error_msg,
                "data": None
            } 