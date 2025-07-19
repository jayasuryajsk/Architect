#!/usr/bin/env python3
"""Quick demo to test if the self-evolving agent is working"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from browser_use.architect.agents.self_evolving_meta_agent import SelfEvolvingMetaAgent

async def test_simple_task():
    """Test with a simple task"""
    print("🧪 Quick Test - Self-Evolving Agent")
    print("="*50)
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ No API key found! Please set GEMINI_API_KEY")
        return
    
    # Simple task that should complete quickly
    task = "Generate a haiku about programming"
    
    print(f"\nTask: {task}")
    print("\n⏳ Processing...")
    
    agent = SelfEvolvingMetaAgent(goal=task)
    
    try:
        result = await agent.run()
        print(f"\n✅ Status: {result.get('status', 'unknown')}")
        print(f"\n📝 Result:\n{result.get('result', 'No result')}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_task())