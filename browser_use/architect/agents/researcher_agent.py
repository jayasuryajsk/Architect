import asyncio
import json
from typing import Any, Dict, List

from browser_use import Agent, Browser, BrowserConfig
from browser_use.architect.memory.memory_manager import log_message
from browser_use.architect.tools.llm_interface import summarize, run_and_parse, _run_llm_with_retry, _run_llm
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from pydantic import SecretStr


class ResearcherAgent:
    def __init__(self, goal: str, model: str = "gemini-1.5-pro"):
        self.name = "Researcher"
        self.goal = goal
        self.model = model

    def _validate_actions(self, actions: List[Dict[str, Any]]) -> None:
        for action in actions:
            if not isinstance(action, dict) or len(action) != 1:
                raise ValueError(f"Invalid action format: {action}")
            action_type, params = next(iter(action.items()))
            if not isinstance(params, dict):
                raise ValueError(f"Params must be a dict: {params}")
            if action_type == "open_url" and not isinstance(params.get("url"), str):
                raise ValueError("open_url needs a string 'url'")
            elif action_type == "wait" and not isinstance(params.get("timeout"), (int, float)):
                raise ValueError("wait needs numeric 'timeout'")
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
      {{ "open_url": {{ "url": "https://developer.chrome.com/docs/extensions/" }} }},
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
- Return only the JSON, no extra text."""

        result = await run_and_parse(prompt, self.model)
        if "error" in result:
            raise ValueError("LLM failed to return valid JSON")

        self._validate_actions(result["parameters"]["action"])
        return result

    async def run(self) -> str:
        log_message(self.name, f"🎯 Starting research: {self.goal}")

        try:
            plan = await self._generate_task_plan()
        except Exception as e:
            log_message(self.name, f"⚠️ Plan generation failed: {e}")
            return await summarize(f"Failed to create task plan: {e}", model=self.model)

        try:
            # First try with browser automation
            browser = Browser(config=BrowserConfig(headless=False))  # Set headless=False to reduce detection
            # Create a LangChain Gemini model for the agent
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro", 
                api_key=SecretStr(gemini_api_key) if gemini_api_key else None
            )
            agent = Agent(task=json.dumps(plan), browser=browser, llm=llm)

            try:
                raw_result = await asyncio.wait_for(agent.run(), timeout=300)
                
                # Check if the result indicates a failure due to bot protection
                if not raw_result or "access denied" in raw_result.lower() or "page crashed" in raw_result.lower():
                    raise ValueError("Browser access denied or page crashed - likely bot protection")
                
                parsed = await _run_llm_with_retry(
                    raw_result, self.model, required_fields=["current_state", "action"]
                )

                if "error" in parsed:
                    raise ValueError(f"Failed to parse result: {parsed}")

                return await summarize(str(parsed), model=self.model)
                
            except (ValueError, asyncio.TimeoutError) as browser_error:
                # Fall back to direct Gemini query when browser automation fails
                log_message(self.name, f"🔄 Browser automation failed: {browser_error}. Falling back to direct Gemini query.")
                
                # Extract the core research question from the goal
                research_topic = self.goal.replace("Research task: ", "").strip()
                fallback_prompt = f"""
                I need information on: {research_topic}
                
                Please provide a comprehensive answer with the latest available information.
                If this is about a scheduled event or future date, please mention how current your information is.
                """
                
                direct_result = await _run_llm(fallback_prompt, self.model)
                return f"[DIRECT GEMINI RESPONSE - Browser automation failed] {direct_result}"

        except Exception as e:
            log_message(self.name, f"❌ Runtime error: {e}")
            return await summarize(f"Agent crashed with error: {e}", model=self.model)

        finally:
            log_message(self.name, f"✅ Completed research on: {self.goal}")
