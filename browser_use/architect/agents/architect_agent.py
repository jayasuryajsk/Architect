import uuid
from browser_use.architect.agents.base_agent import BaseAgent
from browser_use.architect.agents.researcher_agent import ResearcherAgent
from browser_use.architect.memory.memory_manager import log_message, save_task_result
from browser_use.architect.tools.llm_interface import think

class ArchitectAgent(BaseAgent):
    def __init__(self, goal, model="gemini-2.0-flash-lite"):
        super().__init__("Architect", goal, model)

    async def run(self):
        log_message(self.name, f"Received goal: {self.goal}")
        thought = await think(f"Break this goal into a subtask: {self.goal}", self.model)
        subtask = f"Research task: {thought}"
        researcher = ResearcherAgent(goal=subtask, model=self.model)
        result = await researcher.run()
        save_task_result(agent=self.name, task_id=str(uuid.uuid4()), result=result)
        log_message(self.name, f"Completed subtask: {subtask}")
        return result