import asyncio
from typing import List, Dict, Any, Optional, Callable

from browser_use.architect.agents.base_agent import BaseAgent
from browser_use.architect.memory.memory_manager import log_message
from browser_use.architect.tools.llm_interface import summarize

class SummarizerAgent(BaseAgent):
    def __init__(self, goal: str, results: List[Dict[str, Any]], model: str = "gemini-2.0-flash-lite"):
        super().__init__("Summarizer", goal, model)
        self.results = results

    async def run(self, callback: Optional[Callable] = None) -> str:
        log_message(self.name, f"📝 Summarizing {len(self.results)} results")
        
        if callback:
            await callback("start_summarizing", {
                "agent": self.name,
                "count": len(self.results)
            })
        
        try:
            if not self.results:
                log_message(self.name, "⚠️ No results to summarize")
                return "No results available for summarization."
            
            full_text = f"Goal: {self.goal}\n\nResults:\n\n"
            for i, r in enumerate(self.results):
                subtask = r.get("subtask", "Unknown task")
                agent_type = r.get("agent_type", "Unknown agent")
                result = r.get("result", "No result")
                
                full_text += f"### Result {i+1}: [{agent_type}] {subtask}\n{result}\n\n"
            
            if callback:
                await callback("processing", {
                    "agent": self.name,
                    "message": "Generating summary from collected results"
                })
            
            summary = await summarize(full_text, model=self.model)
            log_message(self.name, f"✅ Completed summarization")
            
            if callback:
                await callback("complete", {
                    "agent": self.name,
                    "result": summary
                })
            
            return summary
            
        except Exception as e:
            error_msg = f"Summarization failed: {str(e)}"
            log_message(self.name, f"❌ {error_msg}")
            
            if callback:
                await callback("error", {
                    "agent": self.name,
                    "error": str(e)
                })
            
            return error_msg 