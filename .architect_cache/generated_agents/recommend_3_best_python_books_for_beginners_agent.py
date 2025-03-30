
import asyncio
from typing import Dict, Any, Optional, Callable, List, Union

from browser_use.architect.agents.base.base_agent import BaseAgent
from browser_use.architect.tools.llm_interface import _run_llm_with_retry
from browser_use.architect.memory.memory_manager import log_message

class BookrecommenderAgent(BaseAgent):
    """
    {'description': 'This agent recommends three suitable Python books for beginners.'}
    """
    
    def __init__(self, goal: str, model: str = "gemini-1.5-pro"):
        """
        Initialize a new BookrecommenderAgent.
        
        Args:
            goal: The goal or task for the agent to accomplish
            model: The name of the LLM model to use
        """
        super().__init__("BookRecommender", goal, model)
        
    async def run(self, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Execute the agent to recommend 3 best python books for beginners
        
        Args:
            callback: An optional callback function to report progress
            
        Returns:
            A dictionary containing the result of the agent's execution
        """
        log_message(self.name, f"🚀 Starting {self.name}: {self.goal}")
        
        try:
            # Custom agent implementation
{'error': 'Failed after 3 retries. Last error: Error 400: Expecting value: line 1 column 1 (char 0)', 'status': 'error', 'raw_response': 'python\nimport json\n\ndef implementation(params, **kwargs):\n    """Recommends 3 best Python books for beginners."""\n\n    prompt = "Recommend 3 best Python books for beginners, with a brief description for each and its Amazon link."\n    try:\n        response = _run_llm_with_retry(prompt, stop=["\\n\\n\\n"])\n        books = []\n        for line in response.split(\'\\n\'):\n            if line.strip():  # skip empty lines\n                parts = line.strip().split(" - ")\n                if len(parts) >= 2:  # Make sure there\'s a title and description\n                    title = parts[0].strip()\n                    description_and_link = " - ".join(parts[1:])\n                    try:\n                        description, link = description_and_link.rsplit("(", 1) # Split at last open parenthesis\n                        link = link.rstrip(")") # Remove trailing parenthesis\n                        books.append({"title": title, "description": description.strip(), "link": link.strip()})\n                    except ValueError: # Handle lines without a link gracefully\n                       books.append({"title": title, "description": description_and_link.strip(), "link": ""}) # Add empty link\n\n\n\n        return {"books": books[:3]} # Ensure we only return max 3\n\n    except Exception as e:\n        return {"error": str(e), "books": []}'}
            
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
