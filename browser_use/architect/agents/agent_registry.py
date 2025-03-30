from typing import Dict, Type, Optional, Any
from browser_use.architect.agents.base.base_agent import BaseAgent

class AgentRegistry:
    """
    Central registry for all agent types in the Architect system.
    
    This class manages the mapping between agent names and their implementing classes,
    allowing for dynamic agent instantiation and plugin-like extensibility.
    """
    
    _registry: Dict[str, Type[Any]] = {}
    
    @classmethod
    def register(cls, name: str, agent_class: Type[Any]) -> None:
        """
        Register a new agent type.
        
        Args:
            name: The name to register the agent under
            agent_class: The agent class to register
        """
        if not issubclass(agent_class, BaseAgent):
            raise ValueError(f"Agent class {agent_class.__name__} must inherit from BaseAgent")
            
        cls._registry[name] = agent_class
        
    @classmethod
    def get(cls, name: str) -> Optional[Type[Any]]:
        """
        Get an agent class by name.
        
        Args:
            name: The name of the agent type to get
            
        Returns:
            The agent class if found, None otherwise
        """
        return cls._registry.get(name)
        
    @classmethod
    def list_agents(cls) -> Dict[str, Type[Any]]:
        """
        Get a dictionary of all registered agents.
        
        Returns:
            Dictionary mapping agent names to their classes
        """
        return cls._registry.copy()
        
    @classmethod
    def clear(cls) -> None:
        """Clear all registered agents."""
        cls._registry.clear()

# Import and register all built-in agents
from browser_use.architect.agents.planner_agent import PlannerAgent
from browser_use.architect.agents.researcher_agent import ResearcherAgent
from browser_use.architect.agents.writer_agent import WriterAgent
from browser_use.architect.agents.critic_agent import CriticAgent
from browser_use.architect.agents.summarizer_agent import SummarizerAgent
from browser_use.architect.agents.meta_agent import MetaAgent

# Register built-in agents
AgentRegistry.register("Planner", PlannerAgent)
AgentRegistry.register("Researcher", ResearcherAgent)
AgentRegistry.register("Writer", WriterAgent)
AgentRegistry.register("Critic", CriticAgent)
AgentRegistry.register("Summarizer", SummarizerAgent)
AgentRegistry.register("Meta", MetaAgent) 