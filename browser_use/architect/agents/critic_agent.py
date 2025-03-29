import asyncio
from typing import Any, Dict, Optional, Callable, Union

from browser_use.architect.agents.base_agent import BaseAgent
from browser_use.architect.memory.memory_manager import log_message
from browser_use.architect.tools.llm_interface import _run_llm_with_retry


class CriticAgent(BaseAgent):
    def __init__(self, goal: str, model: str = "gemini-2.0-flash-lite"):
        super().__init__("Critic", goal, model)

    async def refine_goal(self) -> Union[str, Dict[str, str]]:
        """
        Refine the original goal to add clarity, specificity, and context.
        
        Returns:
            Either a string with the refined goal or a dictionary with 'refined' and 'notes' fields
        """
        prompt = f"""
You are a prompt engineering expert specializing in refining vague or general goals
into more specific, actionable prompts with better context.

Original goal: "{self.goal}"

Your task is to refine this goal by:
1. Adding specificity (audience, scope, constraints)
2. Including relevant parameters (metrics, criteria, format preferences)
3. Clarifying the objective
4. Providing context where helpful

Guidelines:
- Preserve the core intent of the original goal
- Add value through specificity, not length
- Make the refined goal more actionable
- Include audience information if appropriate
- Add constraints that make sense for the context

Return your response as a JSON object with two fields:
1. "refined": The refined goal as a clear, concise paragraph
2. "notes": Brief explanation of what you improved and why

Example response format:
{{
  "refined": "As a travel planner for a family of four, recommend five weekend getaway destinations within 3 hours of Boston that offer outdoor activities, family-friendly accommodations, and dining options under $200/night for summer travel.",
  "notes": "Added family context, distance constraint, budget parameter, and seasonal timing."
}}
"""
        
        log_message(self.name, f"🔄 Refining goal: {self.goal}")
        
        try:
            result = await _run_llm_with_retry(prompt, self.model)
            
            # Try to parse as JSON first
            try:
                if isinstance(result, str):
                    import json
                    parsed_result = json.loads(result)
                    if isinstance(parsed_result, dict) and "refined" in parsed_result:
                        refined_goal = parsed_result["refined"]
                        notes = parsed_result.get("notes", "No explanation provided")
                        log_message(self.name, f"✅ Goal refined with notes: {notes}")
                        return {
                            "refined": refined_goal,
                            "notes": notes
                        }
                elif isinstance(result, dict) and "text" in result:
                    # Try to parse the text field as JSON
                    try:
                        import json
                        parsed_text = json.loads(result["text"])
                        if isinstance(parsed_text, dict) and "refined" in parsed_text:
                            refined_goal = parsed_text["refined"]
                            notes = parsed_text.get("notes", "No explanation provided")
                            log_message(self.name, f"✅ Goal refined with notes: {notes}")
                            return {
                                "refined": refined_goal,
                                "notes": notes
                            }
                    except:
                        pass
            except:
                # If JSON parsing fails, continue with string handling
                pass
                
            # Handle string or dict response if JSON parsing failed
            result_text = ""
            if isinstance(result, str):
                result_text = result
            elif isinstance(result, dict) and "text" in result:
                result_text = result["text"]
            else:
                # Convert any other type to string
                result_text = str(result)
                
            result_text = result_text.strip()
            
            if len(result_text) > len(self.goal):
                log_message(self.name, f"✅ Goal refined successfully (plain text)")
                return result_text
            else:
                log_message(self.name, f"⚠️ Refinement unsuccessful, using original goal")
                return self.goal
                
        except Exception as e:
            log_message(self.name, f"❌ Error refining goal: {e}")
            return {
                "status": "error",
                "error": str(e),
                "refined": self.goal
            }
        
    async def run(self, callback: Optional[Callable] = None) -> str:
        """
        Analyze a topic, goal, or set of information through a critical lens.
        
        Args:
            callback: An optional callback function to report progress
            
        Returns:
            A critical analysis of the topic
        """
        log_message(self.name, f"🎯 Starting critical analysis: {self.goal}")
        
        if callback:
            await callback("analyzing", {
                "agent": self.name,
                "goal": self.goal
            })
            
        prompt = f"""
You are a world-class Critical Analysis Expert with exceptional analytical thinking skills.

Provide an in-depth critical analysis of the following prompt:
"{self.goal}"

Your analysis should include:

1. **Strengths:** What makes this prompt effective, clear, or useful?

2. **Weaknesses:** What limitations, ambiguities, or problems does this prompt have?

3. **Areas for Improvement:** How could the prompt be revised to be more effective?

Use detailed, specific observations and recommendations. Format your response using markdown for readability.
Focus on the prompt itself - its structure, clarity, and effectiveness - rather than simply answering the prompt's question.

Provide actionable improvements that would make the prompt more specific, clearer, and more likely to generate a useful response.
"""

        try:
            if callback:
                await callback("processing", {
                    "agent": self.name,
                    "message": "Conducting critical analysis"
                })
                
            result = await _run_llm_with_retry(prompt, self.model)
            
            # Handle string or dict response
            result_text = ""
            if isinstance(result, str):
                result_text = result
            elif isinstance(result, dict) and "text" in result:
                result_text = result["text"]
            else:
                # Convert any other type to string
                result_text = str(result)
                
            log_message(self.name, f"✅ Completed critical analysis")
            
            if callback:
                await callback("complete", {
                    "agent": self.name,
                    "result": result_text
                })
                
            return result_text
            
        except Exception as e:
            error_msg = f"Critical analysis failed: {str(e)}"
            log_message(self.name, f"❌ {error_msg}")
            
            if callback:
                await callback("error", {
                    "agent": self.name,
                    "error": error_msg
                })
                
            return f"Error performing critical analysis: {str(e)}" 