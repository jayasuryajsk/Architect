from typing import List, Dict, Any, Optional, Callable, Union
import asyncio
import json
from datetime import datetime

from browser_use.architect.agents.agent_registry import AgentRegistry
from browser_use.architect.memory.memory_manager import log_message

class PlanExecutor:
    """
    Executes a sequence of agent tasks, managing their dependencies and outputs.
    
    This class handles:
    - Sequential or parallel agent execution
    - Progress tracking and callbacks
    - Output forwarding between agents
    - Error handling and recovery
    """
    
    def __init__(self, plan: List[Dict[str, Any]]):
        """
        Initialize a plan executor.
        
        Args:
            plan: List of task dictionaries, each containing at least:
                {
                    "type": str,  # Agent type name
                    "goal": str,  # Goal for this agent
                    "depends_on": List[str],  # Optional list of task IDs this depends on
                    "id": str,  # Optional unique ID for this task
                }
        """
        self.plan = plan
        self.results: Dict[str, Any] = {}
        self.start_time = None
        self.end_time = None
        
    async def execute(self, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Execute the plan.
        
        Args:
            callback: Optional callback for progress updates
            
        Returns:
            Dictionary containing execution results and metadata
        """
        self.start_time = datetime.now()
        
        try:
            # Track progress
            total_tasks = len(self.plan)
            completed_tasks = 0
            
            for task in self.plan:
                # Get agent type
                agent_type = task["type"]
                agent_cls = AgentRegistry.get(agent_type)
                
                if not agent_cls:
                    raise ValueError(f"Unknown agent type: {agent_type}")
                    
                # Create agent instance
                agent = agent_cls(name=agent_type, goal=task["goal"])
                
                # Report progress
                if callback:
                    await callback("task_start", {
                        "task": task,
                        "progress": f"{completed_tasks}/{total_tasks}"
                    })
                    
                # Execute agent
                try:
                    result = await agent.run()
                    
                    # Store result
                    task_id = task.get("id", f"task_{completed_tasks}")
                    self.results[task_id] = {
                        "task": task,
                        "result": result,
                        "status": "success"
                    }
                    
                except Exception as e:
                    # Handle task failure
                    task_id = task.get("id", f"task_{completed_tasks}")
                    self.results[task_id] = {
                        "task": task,
                        "error": str(e),
                        "status": "error"
                    }
                    
                    log_message("PlanExecutor", f"❌ Task failed: {task_id} - {str(e)}")
                    
                    # Optionally break execution here if task is critical
                    if task.get("critical", False):
                        raise
                        
                completed_tasks += 1
                
                # Report completion
                if callback:
                    await callback("task_complete", {
                        "task": task,
                        "progress": f"{completed_tasks}/{total_tasks}",
                        "result": self.results[task_id]
                    })
                    
            self.end_time = datetime.now()
            
            return {
                "status": "success",
                "results": self.results,
                "metadata": {
                    "start_time": self.start_time.isoformat(),
                    "end_time": self.end_time.isoformat(),
                    "duration": str(self.end_time - self.start_time)
                }
            }
            
        except Exception as e:
            self.end_time = datetime.now()
            
            return {
                "status": "error",
                "error": str(e),
                "partial_results": self.results,
                "metadata": {
                    "start_time": self.start_time.isoformat(),
                    "end_time": self.end_time.isoformat(),
                    "duration": str(self.end_time - self.start_time)
                }
            }
            
    @staticmethod
    def create_plan(tasks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Create a properly formatted plan from a simple task list.
        
        Args:
            tasks: List of simple task dictionaries with type and goal
            
        Returns:
            Properly formatted plan with IDs and metadata
        """
        plan = []
        for i, task in enumerate(tasks):
            plan_task = {
                "id": f"task_{i}",
                "type": task["type"],
                "goal": task["goal"],
                "critical": task.get("critical", False)
            }
            
            # Add dependency on previous task if sequential
            if i > 0:
                plan_task["depends_on"] = [f"task_{i-1}"]
                
            plan.append(plan_task)
            
        return plan 