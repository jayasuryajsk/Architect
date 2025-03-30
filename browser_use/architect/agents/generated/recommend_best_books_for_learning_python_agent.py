
import asyncio
from typing import Dict, Any, Optional, Callable, List, Union

from browser_use.architect.agents.base.base_agent import BaseAgent
from browser_use.architect.tools.llm_interface import _run_llm_with_retry
from browser_use.architect.memory.memory_manager import log_message

class recommend_best_books_for_learning_pythonAgent(BaseAgent):
    """
        {'description': 'This agent recommends books suitable for learning Python, catering to different skill levels and learning styles.'}
    """
    
    def __init__(self, goal: str, model: str = "gemini-1.5-pro"):
        """
        Initialize a new recommend_best_books_for_learning_pythonAgent.
        
        Args:
            goal: The goal or task for the agent to accomplish
            model: The name of the LLM model to use
        """
        super().__init__("Custom", goal, model)
        
    async def run(self, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
                {'description': 'Analyzes user preferences and learning goals to generate a personalized list of recommended books for learning Python.'}
        
        Args:
            callback: An optional callback function to report progress
            
        Returns:
            A dictionary containing the result of the agent's execution
        """
        log_message(self.name, f"🚀 Starting {self.name}: {self.goal}")
        
        try:
            # Custom agent implementation
{'error': 'Failed after 3 retries. Last error: Error 400: Expecting value: line 1 column 1 (char 0)', 'status': 'error', 'raw_response': 'try:\n            if callback:\n                await callback("processing", {\n                    "agent": self.name,\n                    "message": "Starting task"\n                })\n\n            prompt = "Recommend the best books for learning Python, categorized by skill level (beginner, intermediate, advanced).  Include a brief description for each book."\n            log_message(self.name, f"Prompt: {prompt}")\n            response = await _run_llm_with_retry(prompt, self.model)\n            log_message(self.name, f"Response: {response}")\n\n            if callback:\n                await callback("complete", {\n                    "agent": self.name,\n                    "result": response\n                })\n\n            return {\n                "status": "success",\n                "result": response,\n                "agent": self.name,\n                "goal": self.goal\n            }\n\n        except Exception as e:\n            error_msg = f"Failed: {str(e)}"\n            log_message(self.name, error_msg)\n            return {\n                "status": "error",\n                "error": str(e),\n                "result": error_msg\n            }'}
            
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
