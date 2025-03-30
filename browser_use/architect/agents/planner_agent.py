import asyncio
import json
import re
from typing import Any, Dict, List, Optional, Callable

from browser_use.architect.agents.base_agent import BaseAgent
from browser_use.architect.memory.memory_manager import log_message
from browser_use.architect.tools.llm_interface import _run_llm, _run_llm_with_retry


class PlannerAgent(BaseAgent):
    def __init__(self, goal: str, model: str = "gemini-2.0-flash-lite"):
        super().__init__("Planner", goal, model)

    def _enhance_goal_with_persona(self) -> str:
        """
        Enhance the goal with a persona when appropriate to make results more targeted.
        """
        goal = self.goal.lower()
        enhanced_goal = self.goal
        
        # Add persona for travel-related goals
        if any(keyword in goal for keyword in ["trip", "travel", "vacation", "visit", "checklist"]):
            if "norway" in goal or "nordic" in goal or "scandinavia" in goal:
                enhanced_goal = f"{self.goal} for a first-time traveler doing light sightseeing in Northern Norway."
            elif any(country in goal for country in ["japan", "tokyo", "kyoto"]):
                enhanced_goal = f"{self.goal} for a cultural enthusiast interested in both traditional and modern attractions."
            elif any(term in goal for term in ["beach", "tropical", "island", "caribbean"]):
                enhanced_goal = f"{self.goal} for an active traveler who enjoys water sports and outdoor activities."
            else:
                enhanced_goal = f"{self.goal} for a curious traveler who enjoys both popular attractions and off-the-beaten-path experiences."
        
        # Add persona for product research
        elif any(keyword in goal for keyword in ["compare", "review", "best", "top", "recommend", "buy"]):
            enhanced_goal = f"{self.goal} for a discerning buyer who values quality, durability, and value for money."
        
        # Add persona for programming tasks
        elif any(keyword in goal for keyword in ["code", "program", "develop", "script", "software"]):
            enhanced_goal = f"{self.goal} for an intermediate developer who needs well-documented, maintainable code with clear explanations."
        
        # Only log if we actually enhanced the goal
        if enhanced_goal != self.goal:
            log_message(self.name, f"💡 Enhanced goal with persona: {enhanced_goal}")
            
        return enhanced_goal
    
    def _analyze_query_type(self, goal: str) -> str:
        """Analyze the query to determine its general type."""
        goal_lower = goal.lower()
        
        # Programming/coding related
        if any(term in goal_lower for term in ["code", "script", "program", "develop", "python", "javascript", "html", "css", "function", "algorithm"]):
            return "programming"
            
        # Travel/location related
        if any(term in goal_lower for term in ["visit", "travel", "things to do", "places", "attractions", "cities", "destinations", "vacation"]):
            return "travel"
            
        # Product/service review related
        if any(term in goal_lower for term in ["review", "compare", "best", "top", "features", "product", "service", "versus", "vs"]):
            return "product_review"
            
        # Planning/strategy related
        if any(term in goal_lower for term in ["plan", "strategy", "steps", "guide", "how to", "approach", "methodology"]):
            return "planning"
            
        # Content creation related
        if any(term in goal_lower for term in ["write", "create", "compose", "draft", "article", "blog", "essay", "content"]):
            return "content_creation"
            
        # Default to general knowledge
        return "general_knowledge"
    
    async def _create_targeted_plan(self, goal_type: str) -> List[Dict[str, str]]:
        """
        Create a targeted plan based on the type of goal.
        
        Args:
            goal_type: The classified type of goal (e.g., "travel", "research", "coding")
            
        Returns:
            A list of subtasks with agent types and goals
        """
        enhanced_goal = self._enhance_goal_with_persona()
        
        # Travel planning
        if goal_type == "travel":
            return [
                {
                    "agent_type": "Researcher",
                    "goal": f"Research: {enhanced_goal}"
                },
                {
                    "agent_type": "Critic",
                    "goal": f"Analyze key points and structure for {enhanced_goal}"
                },
                {
                    "agent_type": "Writer",
                    "goal": f"Create content for {enhanced_goal}"
                }
            ]
            
        # Programming tasks
        elif goal_type == "coding":
            return [
                {
                    "agent_type": "Researcher",
                    "goal": f"Research best practices and libraries for: {enhanced_goal}"
                },
                {
                    "agent_type": "Critic",
                    "goal": f"Analyze requirements and potential challenges for {enhanced_goal}"
                },
                {
                    "agent_type": "Coder",
                    "goal": f"Implement code for {enhanced_goal}"
                }
            ]
            
        # Content creation/writing
        elif goal_type == "content":
            return [
                {
                    "agent_type": "Researcher",
                    "goal": f"Research: {enhanced_goal}"
                },
                {
                    "agent_type": "Critic",
                    "goal": f"Analyze audience and content structure for {enhanced_goal}"
                },
                {
                    "agent_type": "Writer",
                    "goal": f"Create content for {enhanced_goal}"
                }
            ]
            
        # Product research/comparison
        elif goal_type == "product":
            return [
                {
                    "agent_type": "Researcher",
                    "goal": f"Research products for: {enhanced_goal}"
                },
                {
                    "agent_type": "Critic",
                    "goal": f"Analyze pros and cons of options for {enhanced_goal}"
                },
                {
                    "agent_type": "Writer",
                    "goal": f"Create a comprehensive comparison of {enhanced_goal}"
                }
            ]
            
        # Default research plan
        else:
            return [
                {
                    "agent_type": "Researcher",
                    "goal": f"Research: {enhanced_goal}"
                },
                {
                    "agent_type": "Critic",
                    "goal": f"Analyze and compare options for {enhanced_goal}"
                },
                {
                    "agent_type": "Writer",
                    "goal": f"Create a comprehensive comparison of {enhanced_goal}"
                }
            ]
            
    async def _analyze_goal_type(self) -> str:
        """
        Analyze the goal to determine its type for better planning.
        
        Returns:
            A string representing the goal type: "travel", "coding", "content", "product", or "general"
        """
        prompt = f"""
Analyze the following goal and determine its category from these options:
- "travel" (travel planning, itineraries, packing, destination info)
- "coding" (programming tasks, software development, scripts)
- "content" (writing articles, educational content, creative writing)
- "product" (product research, comparisons, buying guides)
- "general" (anything that doesn't fit the above)

Goal: {self.goal}

Reply with ONLY the category name, no explanation.
"""
        try:
            result = await _run_llm_with_retry(prompt, self.model)
            
            # Handle string or dict response
            goal_type = ""
            if isinstance(result, str):
                goal_type = result.strip().lower()
            elif isinstance(result, dict) and "text" in result:
                goal_type = result["text"].strip().lower()
                
            # Normalize responses
            if "travel" in goal_type:
                goal_type = "travel"
            elif "cod" in goal_type:
                goal_type = "coding"
            elif "content" in goal_type:
                goal_type = "content"
            elif "product" in goal_type:
                goal_type = "product"
            else:
                goal_type = "general"
                
            log_message(self.name, f"🔍 Goal classified as: {goal_type}")
            return goal_type
            
        except Exception as e:
            log_message(self.name, f"⚠️ Error analyzing goal type: {e}. Using 'general' as fallback.")
            return "general"

    async def run(self, callback: Optional[Callable] = None) -> List[Dict[str, str]]:
        """Execute the planning process to create a multi-agent plan."""
        log_message(self.name, f"🎯 Planning execution for goal: {self.goal}")
        
        if callback:
            await callback("planning", {
                "agent": self.name,
                "message": "Creating plan for execution"
            })
        
        try:
            # Step 1: Analyze the type of goal
            goal_type = await self._analyze_goal_type()
            
            # Step 2: Create a targeted plan based on goal type
            subtasks = await self._create_targeted_plan(goal_type)
            
            log_message(self.name, f"✅ Created plan with {len(subtasks)} subtasks")
            
            if callback:
                await callback("plan_created", {
                    "agent": self.name,
                    "subtasks": len(subtasks)
                })
                
            return subtasks
            
        except Exception as e:
            log_message(self.name, f"❌ Planning failed: {e}. Using fallback plan.")
            
            # If planning fails, use a simple fallback plan
            enhanced_goal = self._enhance_goal_with_persona()
            fallback_plan = [
                {
                    "agent_type": "Researcher",
                    "goal": f"Research: {enhanced_goal}"
                },
                {
                    "agent_type": "Critic", 
                    "goal": f"Analyze and compare options for {enhanced_goal}"
                },
                {
                    "agent_type": "Writer",
                    "goal": f"Summarize findings about {enhanced_goal}"
                }
            ]
            
            if callback:
                await callback("fallback_plan", {
                    "agent": self.name,
                    "message": "Using fallback plan due to error",
                    "error": str(e)
                })
                
            return fallback_plan