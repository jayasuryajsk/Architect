import os
import importlib.util
from typing import Dict, Any, Optional, Callable
from browser_use.architect.agents.base_agent import BaseAgent
from browser_use.architect.memory.memory_manager import log_message
from browser_use.architect.tools.llm_interface import _run_llm_with_retry


class MetaAgent(BaseAgent):
    def __init__(self, goal: str, model: str = "gemini-2.0-flash-lite", agent_type: Optional[str] = None):
        """Initialize the MetaAgent."""
        name = "MetaAgent" if agent_type is None else f"{agent_type}Generator"
        super().__init__(name, goal, model)
        self.agent_type = agent_type or ""

    async def run(self, callback: Optional[Callable] = None) -> Dict[str, Any]:
        """Generate and run a custom agent to achieve the goal."""
        try:
            log_message(self.name, f"🚧 Generating agent for: {self.goal}")
            
            if callback:
                await callback("processing", {
                    "agent": self.name,
                    "message": f"Generating agent for: {self.goal}"
                })

            # Generate class and file names
            agent_name = self.goal.strip().replace(" ", "_").replace("-", "_").lower()[:50]  # Limit length
            class_name = "".join(word.capitalize() for word in agent_name.split("_")) + "Agent"
            if self.agent_type:
                class_name = "".join(word.capitalize() for word in self.agent_type.split("_")) + "Agent"
            
            file_name = f"{agent_name}_agent.py"
            file_path = os.path.abspath(os.path.join(
                os.path.dirname(__file__), 
                "generated",
                file_name
            ))

            # Generate agent code
            prompt = f"""
Create a Python agent class to achieve this goal: "{self.goal}"

Requirements:
- Class must inherit from BaseAgent
- Implement async run(self, callback: Optional[Callable] = None) -> Dict[str, Any]
- Use _run_llm_with_retry for task completion
- Log actions with log_message
- Class name: {class_name}
- Return dict with 'status' and 'data' keys
- Include all necessary imports

Example:
from typing import Dict, Any, Optional, Callable
from browser_use.architect.agents.base_agent import BaseAgent
from browser_use.architect.memory.memory_manager import log_message
from browser_use.architect.tools.llm_interface import _run_llm_with_retry

class ExampleAgent(BaseAgent):
    def __init__(self, goal: str, model: str = "gemini-2.0-flash-lite"):
        super().__init__("ExampleAgent", goal, model)
        
    async def run(self, callback: Optional[Callable] = None) -> Dict[str, Any]:
        log_message(self.name, f"Starting task: {self.goal}")
        
        if callback:
            await callback("processing", {
                "agent": self.name,
                "message": "Processing request"
            })
        
        response = await _run_llm_with_retry(self.goal, model=self.model)
        
        if isinstance(response, dict) and "text" in response:
            response = response["text"]
        
        result = {
            "status": "success",
            "data": response
        }
        
        if callback:
            await callback("completed", {
                "agent": self.name,
                "result": result
            })
        
        return result
"""
            # Get code from LLM
            code = await _run_llm_with_retry(prompt, self.model)
            if isinstance(code, dict):
                code = code.get("text", "") or code.get("raw_response", "")
            
            # Clean up code formatting
            if "```python" in code:
                code = code.split("```python", 1)[1].split("```", 1)[0]
            elif "```" in code:
                code = code.split("```", 1)[1].split("```", 1)[0]
            code = code.strip()
            
            if "class " not in code:
                raise ValueError("Generated code does not contain a class definition")

            # Save and load agent
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                f.write(code)
            
            log_message(self.name, f"📝 Created agent at {file_path}")
            
            # Load and run agent
            spec = importlib.util.spec_from_file_location(class_name, file_path)
            if not spec or not spec.loader:
                raise ImportError(f"Failed to load module from {file_path}")
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            agent_class = getattr(module, class_name)
            agent = agent_class(goal=self.goal)
            
            log_message(self.name, f"🚀 Running {class_name}...")
            result = await agent.run(callback=callback)
            
            return {
                "status": "success",
                "data": result
            }
            
        except Exception as e:
            error_msg = f"Failed to generate/run agent: {str(e)}"
            log_message(self.name, f"❌ {error_msg}")
            
            if callback:
                await callback("error", {
                    "agent": self.name,
                    "error": error_msg
                })
            
            return {
                "status": "error",
                "error": error_msg
            }