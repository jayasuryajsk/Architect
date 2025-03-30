import asyncio
from typing import Any, Dict, Optional, Callable

from browser_use.architect.agents.base_agent import BaseAgent
from browser_use.architect.memory.memory_manager import log_message
from browser_use.architect.tools.llm_interface import _run_llm


class WriterAgent(BaseAgent):
    def __init__(self, goal: str, model: str = "gemini-2.0-flash-lite"):
        super().__init__("Writer", goal, model)

    async def run(self, callback: Optional[Callable] = None) -> str:
        log_message(self.name, f"✍️ Writing: {self.goal}")
        
        if callback:
            await callback("writer_start", {
                "agent": self.name,
                "goal": self.goal
            })
        
        prompt = f"""
You are a professional writer.

Write the following content:
"{self.goal}"

Your writing should be:
- Clear and concise
- Well-organized with appropriate structure
- Engaging and easy to read
- Free of errors

Provide only the requested content, without any additional commentary.
"""

        try:
            if callback:
                await callback("processing", {
                    "agent": self.name,
                    "message": "Drafting content"
                })
                
            result = await _run_llm(prompt, self.model)
            log_message(self.name, f"✅ Writing complete: {self.goal}")
            
            if callback:
                await callback("complete", {
                    "agent": self.name,
                    "result": result
                })
                
            return result
            
        except Exception as e:
            log_message(self.name, f"❌ Writing failed: {e}")
            
            if callback:
                await callback("error", {
                    "agent": self.name,
                    "error": str(e)
                })
                
            return f"Writing failed with error: {str(e)}" 