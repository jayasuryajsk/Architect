import asyncio
import json
import os
from typing import Any, Dict, Optional

import google.generativeai as genai

# Configure with API key from env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class RetryError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Error {status_code}: {message}")

async def run_and_parse(prompt: str, model: str = "gemini-1.5-pro") -> Dict[str, Any]:
    """Run Gemini and parse the output as JSON if possible."""
    try:
        model_instance = genai.GenerativeModel(model_name=model)
        response = model_instance.generate_content(prompt)
        content = response.text.strip()

        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()

        return json.loads(content)

    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "raw_response": content if "content" in locals() else None
        }

async def _run_llm_with_retry(prompt: str, model: str = "gemini-1.5-pro", max_retries: int = 3, required_fields: Optional[list[str]] = None) -> Dict[str, Any]:
    attempt = 0
    last_error = None
    last_response = None
    result = None

    while attempt <= max_retries:
        try:
            if attempt > 0:
                retry_context = f"\n\n⚠️ Previous attempt {attempt} failed: {str(last_error)}\n"
                retry_context += "Please ensure your response is valid JSON."
                if required_fields:
                    retry_context += f"\nRequired fields: {', '.join(required_fields)}"
                prompt = retry_context + "\n\n" + prompt

            result = await run_and_parse(prompt, model)

            if "error" in result:
                raise RetryError(result["error"])

            if required_fields:
                missing = [field for field in required_fields if field not in result]
                if missing:
                    raise RetryError(f"Missing required fields: {', '.join(missing)}")

            return result

        except RetryError as e:
            last_error = str(e)
            last_response = result.get("raw_response") if result else None
        
        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"
            last_response = str(result) if result else None

        attempt += 1
        await asyncio.sleep(2 ** attempt)

    return {
        "error": f"Failed after {max_retries} retries. Last error: {last_error}",
        "status": "error",
        "raw_response": last_response
    }

async def _run_llm(prompt: str, model: str = "gemini-1.5-pro") -> str:
    try:
        model_instance = genai.GenerativeModel(model_name=model)
        response = model_instance.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        retry_msg = f"⚠️ LLM error: {e}\n\nRetrying with fallback prompt..."
        try:
            fallback_prompt = f"{retry_msg}\n\nOriginal prompt:\n{prompt}"
            model_instance = genai.GenerativeModel(model_name=model)
            response = model_instance.generate_content(fallback_prompt)
            return response.text.strip()
        except Exception as second_error:
            return f"❌ LLM failed twice: {second_error}"

async def think(prompt: str, model: str = "gemini-1.5-pro") -> str:
    return await _run_llm(f"Think about this:\n{prompt}", model)

async def summarize(text: str, model: str = "gemini-1.5-pro") -> str:
    return await _run_llm(f"Summarize the following text:\n{text}", model)
