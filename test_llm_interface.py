#!/usr/bin/env python3
"""Test the LLM interface directly"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Configure API before importing
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

from browser_use.architect.tools.llm_interface import run_and_parse

async def test_llm():
    print("🧪 Testing LLM Interface")
    print(f"API Key: {os.getenv('GEMINI_API_KEY')[:10]}...")
    
    prompt = """
    Generate a JSON response with:
    {
        "message": "Hello from Gemini",
        "timestamp": "2024-01-01"
    }
    """
    
    try:
        print("⏳ Calling LLM...")
        result = await run_and_parse(prompt, model="gemini-2.5-flash")
        print(f"✅ Result: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_llm())