import asyncio
from typing import Any, Dict, Optional, Callable

from browser_use.architect.agents.base_agent import BaseAgent
from browser_use.architect.memory.memory_manager import log_message
from browser_use.architect.tools.llm_interface import _run_llm


class CoderAgent(BaseAgent):
    def __init__(self, goal: str, model: str = "gemini-2.0-flash-lite"):
        super().__init__("Coder", goal, model)

    async def run(self, callback: Optional[Callable] = None) -> str:
        log_message(self.name, f"🧑‍💻 Coding task: {self.goal}")
        
        if callback:
            await callback("coder_start", {
                "agent": self.name,
                "goal": self.goal
            })
        
        prompt = f"""
You are an expert programmer.

Generate code for the following:
"{self.goal}"

Your code should be:
- Clean, efficient, and well-structured
- Well-documented with comments where necessary
- Include explanations of logic and design choices
- Include examples of usage (if applicable)

Provide only the requested code and explanations, no additional commentary.
"""

        try:
            if callback:
                await callback("processing", {
                    "agent": self.name,
                    "message": "Writing code"
                })
                
            result = await _run_llm(prompt, self.model)
            log_message(self.name, f"✅ Code generation complete")
            
            if callback:
                await callback("complete", {
                    "agent": self.name,
                    "result": result
                })
                
            return result
            
        except Exception as e:
            log_message(self.name, f"❌ Code generation failed: {e}")
            
            if callback:
                await callback("error", {
                    "agent": self.name,
                    "error": str(e)
                })
                
            return f"Code generation failed with error: {str(e)}" 