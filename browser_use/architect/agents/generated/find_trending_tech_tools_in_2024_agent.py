from typing import Dict, Any, Optional, Callable
from browser_use.architect.agents.base_agent import BaseAgent
from browser_use.architect.memory.memory_manager import log_message
from browser_use.architect.tools.llm_interface import _run_llm_with_retry
import json

class FindTrendingTechToolsIn2024Agent(BaseAgent):
    def __init__(self, goal: str, model: str = "gemini-2.0-flash-lite"):
        super().__init__("FindTrendingTechToolsIn2024Agent", goal, model)

    async def run(self, callback: Optional[Callable] = None) -> Dict[str, Any]:
        log_message(self.name, f"Starting task: {self.goal}")

        if callback:
            await callback("processing", {
                "agent": self.name,
                "message": "Processing request"
            })

        try:
            prompt = "List 5 trending tech tools in 2024. Provide a short description of each tool, including its main use case. Return the response in JSON format with a list of dictionaries where each dictionary contains the tool name and description."
            response = await _run_llm_with_retry(self.model, prompt)
            
            try:
                tools = json.loads(response)
            except json.JSONDecodeError:
                log_message(self.name, f"Error: Could not parse LLM response as JSON. Response: {response}")
                return {
                    "status": "error",
                    "result": "Failed to parse LLM response."
                }


            if not isinstance(tools, list):
                log_message(self.name, f"Error: LLM response is not a list. Response: {response}")
                return {
                    "status": "error",
                    "result": "LLM response is not a list of tools."
                }

            result = tools
            log_message(self.name, f"Successfully found trending tech tools.")

        except Exception as e:
            log_message(self.name, f"An error occurred: {e}")
            return {
                "status": "error",
                "result": str(e)
            }

        if callback:
            await callback("completed", {
                "agent": self.name,
                "result": result
            })

        return {
            "status": "success",
            "result": result
        }