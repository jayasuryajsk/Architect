
import asyncio
from typing import Dict, Any, Optional, Callable, List, Union

from browser_use.architect.agents.base.base_agent import BaseAgent
from browser_use.architect.tools.llm_interface import _run_llm_with_retry
from browser_use.architect.memory.memory_manager import log_message

class BookRecommenderAgent(BaseAgent):
    """An agent that recommends books for learning Python.
    
    This agent uses an LLM to complete the task without browser automation."""
    
    def __init__(self, goal: str, model: str = "gemini-2.0-flash-lite"):
        """Initialize a new BookRecommenderAgent.
        
        Args:
            goal: The goal or task for the agent to accomplish
            model: The name of the LLM model to use
        """
        super().__init__("BookRecommender", goal, model)
        
    async def run(self, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Recommend books for learning Python.
        
        Args:
            callback: An optional callback function to report progress
            
        Returns:
            A dictionary containing the result of the agent's execution
        """
        log_message(self.name, f"🚀 Starting {self.name}: {self.goal}")
        
        try:
            if callback:
                await callback("processing", {
                    "agent": self.name,
                    "message": "Generating book recommendations"
                })
                
            prompt = f"""
You are a skilled BookRecommender agent tasked with: {self.goal}

Provide a list of exactly 3 highly-recommended books for beginners learning Python. 
For each book, include:
1. Title and author
2. Why it's good for beginners
3. Key topics covered
4. Publication date or latest edition
5. A link to purchase or access it (if available)

Format your response as a neat, organized list with clear headings and bullet points.
"""
            
            # Use LLM to generate a response
            result = await _run_llm_with_retry(prompt, self.model)
            
            if callback:
                await callback("complete", {
                    "agent": self.name,
                    "result": result
                })
            
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
