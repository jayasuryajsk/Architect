
import asyncio
from typing import Dict, Any, Optional, Callable, List, Union

from browser_use.architect.agents.base.base_agent import BaseAgent
from browser_use.architect.tools.llm_interface import _run_llm_with_retry
from browser_use.architect.memory.memory_manager import log_message

class CustomAgent(BaseAgent):
    """
    {'description': 'This agent recommends books suitable for learning Python programming.'}
    """
    
    def __init__(self, goal: str, model: str = "gemini-1.5-pro"):
        """
        Initialize a new CustomAgent.
        
        Args:
            goal: The goal or task for the agent to accomplish
            model: The name of the LLM model to use
        """
        super().__init__("Custom", goal, model)
        
    async def run(self, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Execute the agent to recommend best books for learning python
        
        Args:
            callback: An optional callback function to report progress
            
        Returns:
            A dictionary containing the result of the agent's execution
        """
        log_message(self.name, f"🚀 Starting {self.name}: {self.goal}")
        
        try:
            # Custom agent implementation
{'error': 'Failed after 3 retries. Last error: Error 400: Expecting value: line 1 column 1 (char 0)', 'status': 'error', 'raw_response': 'python\nimport json\nfrom typing import Any, Dict, List\n\nfrom browser_automation import BrowserAutomation\n\ndef implementation(params: Dict[str, Any]) -> Dict[str, Any]:\n    try:\n        recommendations = _run_llm_with_retry(\n            "Provide a JSON array of objects, where each object represents a book recommendation for learning Python. Each object should contain the following keys: \'title\', \'author\', \'description\', \'level\' (beginner, intermediate, or advanced).",\n            stop=["'}
            
            log_message(self.name, f"✅ Completed task successfully")
            return {
                "status": "success",
                "result": result,
                "agent": self.name,
                "goal": self.goal
            }
            
        except Exception as e:
            error_msg = f"Failed to complete task: {str(e)}"
            log_message(self.name, f"❌ {error_msg}")
            return {
                "status": "error",
                "error": str(e),
                "result": error_msg,
                "agent": self.name,
                "goal": self.goal
            }
