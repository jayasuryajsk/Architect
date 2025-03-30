import asyncio
import json
from typing import Any, Dict, List

from browser_use import Agent, Browser, BrowserConfig
from browser_use.architect.agents.base_agent import BaseAgent
from browser_use.architect.memory.memory_manager import log_message
from browser_use.architect.tools.llm_interface import summarize, run_and_parse, _run_llm_with_retry, _run_llm
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from pydantic import SecretStr


class ResearcherAgent(BaseAgent):
    def __init__(self, goal: str, model: str = "gemini-2.0-flash-lite"):
        super().__init__("Researcher", goal, model)

    def _validate_actions(self, actions: List[Dict[str, Any]]) -> None:
        for action in actions:
            if not isinstance(action, dict) or len(action) != 1:
                raise ValueError(f"Invalid action format: {action}")
            action_type, params = next(iter(action.items()))
            if not isinstance(params, dict):
                raise ValueError(f"Params must be a dict: {params}")
            if action_type == "open_url" and not isinstance(params.get("url"), str):
                raise ValueError("open_url needs a string 'url'")
            elif action_type == "wait":
                if not isinstance(params.get("timeout"), (int, float)):
                    raise ValueError("wait needs numeric 'timeout'")
                # Enforce reasonable wait time (max 30 seconds in milliseconds)
                if params.get("timeout", 0) > 30000:
                    params["timeout"] = 5000
                    log_message(self.name, f"⚠️ Wait time too long, limiting to 5000ms")
            elif action_type in {"click_element", "scroll_to"} and not isinstance(params.get("selector"), str):
                raise ValueError(f"{action_type} needs a string 'selector'")
            elif action_type == "extract_content":
                if not isinstance(params.get("selector"), str) or not isinstance(params.get("attribute"), str):
                    raise ValueError("extract_content needs string 'selector' and 'attribute'")

    async def _generate_task_plan(self) -> Dict[str, Any]:
        prompt = f"""You are a browser automation agent. Generate a valid JSON plan for this goal:

GOAL: {self.goal}

Respond ONLY with this format:

{{
  "name": "AgentOutput",
  "parameters": {{
    "action": [
      {{ "open_url": {{ "url": "https://www.google.com/search?q=ai+image+generators+features" }} }},
      {{ "wait": {{ "timeout": 2000 }} }},
      {{ "extract_content": {{ "selector": "main", "attribute": "text" }} }}
    ],
    "current_state": {{
      "evaluation_previous_goal": "Starting research",
      "memory": "Starting research on: {self.goal}",
      "next_goal": "Extract and analyze relevant information"
    }}
  }}
}}

Rules:
- Use only supported actions: open_url, wait, click_element, scroll_to, extract_content
- One action per dictionary
- Parameters must be correctly typed
- Return only the JSON, no extra text
- For wait action, timeout is in MILLISECONDS (1000ms = 1 second). Never use more than 5000ms (5 seconds)."""

        result = await run_and_parse(prompt, self.model)
        if "error" in result:
            raise ValueError("LLM failed to return valid JSON")

        self._validate_actions(result["parameters"]["action"])
        return result

    async def run(self, callback=None) -> str:
        log_message(self.name, f"🎯 Starting research: {self.goal}")

        if callback:
            await callback("research_start", {
                "agent": self.name,
                "goal": self.goal
            })

        try:
            plan = await self._generate_task_plan()
        except Exception as e:
            log_message(self.name, f"⚠️ Plan generation failed: {e}")
            
            if callback:
                await callback("error", {
                    "agent": self.name,
                    "error": f"Plan generation failed: {e}"
                })
                
            return await summarize(f"Failed to create task plan: {e}", model=self.model)

        try:
            # First try with browser automation
            browser = Browser(config=BrowserConfig(headless=False))  # Set headless=False to reduce detection
            # Create a LangChain Gemini model for the agent
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash-lite", 
                api_key=SecretStr(gemini_api_key) if gemini_api_key else None
            )
            agent = Agent(task=json.dumps(plan), browser=browser, llm=llm)

            try:
                raw_result = await asyncio.wait_for(agent.run(), timeout=300)
                
                # Check if the result indicates a failure due to bot protection
                # Using safer string checking to prevent .lower() on non-string objects
                if not raw_result:
                    log_message(self.name, f"⚠️ Browser returned empty result")
                    return "Browser automation encountered an issue with empty results. Please try a different search query or approach."
                
                # Make sure we're dealing with a string before calling .lower()
                if isinstance(raw_result, str):
                    result_lower = raw_result.lower()
                    if "access denied" in result_lower or "page crashed" in result_lower:
                        log_message(self.name, f"⚠️ Browser access issue: {raw_result}")
                        return "Browser automation encountered access issues. Please try a different search query or approach."
                else:
                    # If raw_result is not a string, handle it appropriately
                    log_message(self.name, f"⚠️ Browser returned non-string result: {type(raw_result)}")
                    raw_result = str(raw_result)  # Convert to string for further processing
                
                parsed = await _run_llm_with_retry(
                    raw_result, self.model, required_fields=["current_state", "action"]
                )

                if "error" in parsed:
                    log_message(self.name, f"⚠️ Failed to parse result: {parsed}")
                    return f"Error parsing browser results: {parsed.get('error', 'Unknown parsing error')}"

                return await summarize(str(parsed), model=self.model)
                
            except (ValueError, asyncio.TimeoutError) as browser_error:
                # Instead of falling back, return the error
                log_message(self.name, f"❌ Browser automation failed: {browser_error}.")
                return f"Browser automation failed: {browser_error}. Please try again with a different query."

        except Exception as e:
            log_message(self.name, f"❌ Runtime error: {e}")
            return await summarize(f"Agent crashed with error: {e}", model=self.model)

        finally:
            log_message(self.name, f"✅ Completed research on: {self.goal}")
