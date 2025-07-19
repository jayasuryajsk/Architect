#!/usr/bin/env python3
"""Test with timeout to see where it's hanging"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from browser_use.architect.agents.self_evolving_meta_agent import SelfEvolvingMetaAgent

async def run_with_timeout():
    print("🧪 Testing Self-Evolving Agent with timeout")
    
    # Very simple task
    task = "What is 2 + 2?"
    
    print(f"\nTask: {task}")
    print("⏳ Processing (10 second timeout)...")
    
    agent = SelfEvolvingMetaAgent(goal=task)
    
    try:
        # Run with 10 second timeout
        result = await asyncio.wait_for(
            agent.run(),
            timeout=10.0
        )
        print(f"✅ Result: {result}")
    except asyncio.TimeoutError:
        print("❌ Timed out after 10 seconds")
        print("\nPossible issues:")
        print("- LLM calls are taking too long")
        print("- The model name might be incorrect")
        print("- Network connectivity issues")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_with_timeout())