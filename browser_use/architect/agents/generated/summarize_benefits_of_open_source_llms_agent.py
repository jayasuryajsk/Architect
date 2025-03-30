from typing import Dict, Any, Optional, Callable
from browser_use.architect.agents.base_agent import BaseAgent
from browser_use.architect.memory.memory_manager import log_message
from browser_use.architect.tools.llm_interface import _run_llm_with_retry

class ResearchsummarizerAgent(BaseAgent):
    def __init__(self, goal: str, model: str = "gemini-2.0-flash-lite"):
        super().__init__("ResearchsummarizerAgent", goal, model)
        
    async def run(self, callback: Optional[Callable] = None) -> Dict[str, Any]:
        log_message(self.name, f"Starting task: {self.goal}")
        
        if callback:
            await callback("processing", {
                "agent": self.name,
                "message": "Processing request"
            })
            
        try:
            prompt = f"Summarize the key benefits of using open-source LLMs. Provide a concise and informative summary."
            response = await _run_llm_with_retry(prompt, model=self.model)
            
            if isinstance(response, dict) and "text" in response:
                response = response["text"]
            
            result = {
                "status": "success",
                "data": response
            }
            
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            log_message(self.name, f"❌ {error_message}")
            result = {
                "status": "error",
                "message": error_message
            }
        
        if callback:
            await callback("completed", {
                "agent": self.name,
                "result": result
            })
            
        return result