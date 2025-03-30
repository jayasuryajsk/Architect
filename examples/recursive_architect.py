#!/usr/bin/env python
"""
Recursive Architect Example - Demonstrates the Architect's recursive planning capabilities

This example shows how the ArchitectAgent breaks down complex goals into subtasks,
assigns specialized agents to each subtask, and then synthesizes the results.

Usage:
    python examples/recursive_architect.py

Requirements:
    - Set GEMINI_API_KEY in .env or as environment variable
"""

import asyncio
import os
from dotenv import load_dotenv

from browser_use.architect.agents.architect_agent import ArchitectAgent
from browser_use.architect.memory.memory_manager import log_message

# Load environment variables
load_dotenv()

async def run_example():
    """Run an example of the recursive architect."""
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️ GEMINI_API_KEY not found. Please set it in .env file or environment.")
        return
    
    # Define a complex goal that requires multiple agents
    goal = """Analyze the current trends in AI image generation models, 
    compare the top 3 options, and suggest which one might be best for a 
    small design agency. Include estimated costs where available."""
    
    print("=" * 80)
    print(f"🎯 GOAL: {goal}")
    print("=" * 80)
    print("\n🚀 Starting Architect with recursive planning...\n")
    
    # Create and run the Architect agent
    architect = ArchitectAgent(goal=goal, model="gemini-2.0-flash-lite")
    
    # Run the architect and get the final result
    result = await architect.run()
    
    print("\n" + "=" * 80)
    print("📋 FINAL RESULT:")
    print("=" * 80)
    print(result)
    print("=" * 80)
    
    return result

if __name__ == "__main__":
    asyncio.run(run_example()) 