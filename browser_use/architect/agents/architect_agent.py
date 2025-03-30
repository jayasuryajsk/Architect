import uuid
from typing import Callable, Optional, List, Dict, Any

from browser_use.architect.agents.base_agent import BaseAgent
from browser_use.architect.agents.planner_agent import PlannerAgent
from browser_use.architect.agents.researcher_agent import ResearcherAgent
from browser_use.architect.agents.critic_agent import CriticAgent
from browser_use.architect.agents.writer_agent import WriterAgent
from browser_use.architect.agents.coder_agent import CoderAgent
from browser_use.architect.agents.summarizer_agent import SummarizerAgent
from browser_use.architect.agents.meta_agent import MetaAgent
from browser_use.architect.memory.memory_manager import log_message, save_task_result


class ArchitectAgent(BaseAgent):
    def __init__(self, goal: str, model: str = "gemini-2.0-flash-lite"):
        super().__init__("Architect", goal, model)

    async def run(self, callback: Optional[Callable] = None):
        log_message(self.name, f"📌 Received high-level goal: {self.goal}")

        # Step 1: Use PlannerAgent to break goal into subtasks
        planner = PlannerAgent(goal=self.goal, model=self.model)
        log_message(self.name, f"🔄 Running PlannerAgent to create subtasks")
        
        try:
            subtasks = await planner.run(callback=callback)
            log_message(self.name, f"✅ Planning complete. Created {len(subtasks)} subtasks")
        except Exception as e:
            log_message(self.name, f"❌ PlannerAgent failed: {e}")
            # Return error but don't terminate
            return [{
                "agent": "Planner",
                "goal": self.goal,
                "result": f"Error in planning: {str(e)}"
            }]

        results = []
        for idx, task in enumerate(subtasks):
            try:
                agent_type = task["agent_type"]
                subgoal = task["goal"]
                agent_name = f"{agent_type}-{idx+1}"
                log_message(self.name, f"🧠 Spawning agent: {agent_name} with goal: {subgoal}")

                if callback:
                    await callback("spawn_agent", {
                        "agent_type": agent_type,
                        "goal": subgoal,
                        "index": idx + 1
                    })

                agent = self._create_agent(agent_type, subgoal)
                if not agent:
                    log_message(self.name, f"❌ Unknown agent type: {agent_type}")
                    result = f"Error: Unknown agent type '{agent_type}'"
                    agent_name = f"Unknown-{agent_type}"
                else:
                    agent_name = agent.name
                    try:
                        log_message(self.name, f"🔄 Starting execution of {agent_name}")
                        result = await agent.run(callback)
                        
                        # Check if result indicates a browser error
                        if isinstance(result, str) and "Browser automation failed" in result:
                            log_message(self.name, f"⚠️ {agent_name} encountered browser issues: {result[:100]}...")
                        else:
                            log_message(self.name, f"✅ Got result from {agent_name}")
                            
                    except Exception as e:
                        result = f"[Error while executing subtask]: {str(e)}"
                        log_message(self.name, f"❌ Error in {agent_name}: {e}")

                results.append({
                    "agent": agent_name,
                    "goal": subgoal,
                    "result": result
                })

                task_id = str(uuid.uuid4())
                log_message(self.name, f"💾 Saving result for {agent_name} with task ID: {task_id[:8]}...")
                save_task_result(
                    agent=agent_name,
                    task_id=task_id,
                    result=result
                )

                if callback:
                    await callback("agent_complete", {
                        "agent": agent_name,
                        "goal": subgoal,
                        "result": result
                    })
            except Exception as task_error:
                # Catch any unexpected errors in the task processing loop
                log_message(self.name, f"❌ Critical error processing task {idx+1}: {task_error}")
                results.append({
                    "agent": f"Task-{idx+1}",
                    "goal": task.get("goal", "Unknown goal"),
                    "result": f"Critical error: {str(task_error)}"
                })

        # Step 3: Run SummarizerAgent to compile results if we have multiple results
        if len(results) > 1:
            try:
                log_message(self.name, f"🔄 Running SummarizerAgent to compile results")
                
                # Convert results to the format expected by SummarizerAgent
                formatted_results = []
                for r in results:
                    formatted_results.append({
                        "subtask": r.get("goal", "Unknown goal"),
                        "agent_type": r.get("agent", "Unknown").split("-")[0],
                        "result": r.get("result", "No result")
                    })
                
                # Create SummarizerAgent with the results in the constructor
                summarizer = SummarizerAgent(
                    goal=self.goal, 
                    results=formatted_results,
                    model=self.model
                )
                
                # Run the summarizer
                summary = await summarizer.run(callback=callback)
                
                results.append({
                    "agent": "Summarizer",
                    "goal": f"Summarize results for: {self.goal}",
                    "result": summary
                })
                
                log_message(self.name, f"✅ Summary generated successfully")
            except Exception as e:
                log_message(self.name, f"❌ SummarizerAgent failed: {e}")
                results.append({
                    "agent": "Summarizer",
                    "goal": f"Summarize results for: {self.goal}",
                    "result": f"Error generating summary: {str(e)}"
                })

        # Final log
        log_message(self.name, f"✅ All subtasks complete for goal: {self.goal}")
        return results

    def _create_agent(self, agent_type: str, subgoal: str) -> BaseAgent:
        """
        Creates and returns an agent based on the specified type to fulfill a subgoal.
        
        Args:
            agent_type: The type of agent to create
            subgoal: The goal to assign to the agent
            
        Returns:
            An initialized agent of the specified type
        """
        log_message(self.name, f"Creating {agent_type}Agent for: {subgoal}")
        
        if agent_type.lower() == "researcher":
            return ResearcherAgent(subgoal, self.model)
        elif agent_type.lower() == "writer":
            return WriterAgent(subgoal, self.model)
        elif agent_type.lower() == "critic":
            return CriticAgent(subgoal, self.model)
        elif agent_type.lower() == "planner":
            return PlannerAgent(subgoal, self.model)
        elif agent_type.lower() == "coder":
            return CoderAgent(subgoal, self.model)
        elif agent_type.lower() == "summarizer":
            # For summarizer, we need to provide results later
            # Creating with empty results that will be updated before running
            return SummarizerAgent(goal=self.goal, results=[], model=self.model)
        else:
            log_message(self.name, f"Unknown agent type '{agent_type}', using MetaAgent")
            # Use MetaAgent for unknown agent types
            return MetaAgent(goal=subgoal, model=self.model, agent_type=agent_type)