#!/usr/bin/env python3
"""Simple test of the V2 agent with better error handling"""

import asyncio
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()

# Instead of using the complex V2, let's test with a simpler approach
from browser_use.architect.agents.self_evolving_agent_v2 import SelfEvolvingAgentV2

async def simple_test():
    """Test with a task that doesn't require tool generation"""
    agent = SelfEvolvingAgentV2()
    
    # Use a simple search task that uses existing tools
    task = "Search for Python programming tutorials"
    
    print(f"\n📋 Task: {task}")
    
    try:
        result = await agent.run(task, max_duration_hours=0.05)  # 3 minutes
        
        if result.get('success'):
            print("\n✅ Success!")
            print(f"Result: {result.get('result', 'No result')[:200]}...")
        else:
            print(f"\n❌ Failed: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(simple_test())