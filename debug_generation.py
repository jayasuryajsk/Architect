#!/usr/bin/env python3
"""Debug code generation"""

import asyncio
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

async def test_simple_generation():
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.5-pro')
    
    prompt = """
Generate a simple Python async function that counts words in text.

Requirements:
- Function name: count_words
- Parameter: text (string)
- Returns: dict with 'result' containing word count
- Use async def
- Include proper indentation

Return ONLY the function code:
"""
    
    response = model.generate_content(prompt)
    code = response.text.strip()
    
    print("Generated code:")
    print("=" * 60)
    print(repr(code))  # Show with escape characters
    print("=" * 60)
    print(code)
    print("=" * 60)
    
    # Try to parse it
    try:
        import ast
        ast.parse(code)
        print("✅ Syntax is valid!")
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_generation())