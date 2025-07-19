#!/usr/bin/env python3
"""Test basic API functionality"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def test_api():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ No API key found!")
        return
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    genai.configure(api_key=api_key)
    
    # Test both models
    models = ['gemini-2.5-flash', 'gemini-2.5-pro']
    
    for model_name in models:
        print(f"\n{'='*40}")
        print(f"Testing {model_name}")
        print('='*40)
        
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say 'Hello, I'm working!'")
            print(f"✅ API Response: {response.text}")
        except Exception as e:
            print(f"❌ API Error: {e}")

if __name__ == "__main__":
    test_api()