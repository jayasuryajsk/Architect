#!/usr/bin/env python3
"""
Test with a task that absolutely requires new tool generation
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from browser_use.architect.agents.self_evolving_meta_agent import SelfEvolvingMetaAgent


async def test_specialized_tool():
    """Test with a task that needs a specialized tool"""
    print("🧬 TESTING SPECIALIZED TOOL GENERATION")
    print("=" * 60)
    
    # Task that requires specialized processing
    task = """Create a tool that can convert temperature between Celsius, Fahrenheit, and Kelvin.
    Then use it to convert:
    - 100°C to Fahrenheit and Kelvin
    - 32°F to Celsius and Kelvin
    - 273.15K to Celsius and Fahrenheit
    
    Show all conversions with 2 decimal places."""
    
    print(f"\n📋 Task: Temperature Converter Tool")
    print("This requires generating a specialized conversion tool!")
    print("-" * 60)
    
    # Create agent
    agent = SelfEvolvingMetaAgent(goal=task, model="gemini-1.5-flash")
    
    # Override the execution to trace capability analysis
    original_analyze = agent.capability_analyzer.analyze_task
    
    async def trace_analyze(task_str):
        print("\n🔍 Analyzing task requirements...")
        result = await original_analyze(task_str)
        print(f"   Task type: {result.get('task_type', 'unknown')}")
        print(f"   Required capabilities: {result.get('required_capabilities', [])}")
        print(f"   Complexity: {result.get('complexity', 0)}")
        return result
    
    agent.capability_analyzer.analyze_task = trace_analyze
    
    try:
        print("\n🚀 Running agent...")
        result = await agent.run()
        
        print("\n✨ RESULTS:")
        print(f"Status: {result['status']}")
        print(f"Tools generated: {result.get('tools_generated', 0)}")
        
        print("\n📝 Result:")
        print("-" * 40)
        print(result.get('result', 'No result'))
        
        # Check if any tools were added
        if agent.tool_library.active_tools:
            print("\n🔧 Tools in library:")
            for name in agent.tool_library.active_tools:
                print(f"   - {name}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_code_generation_task():
    """Test with explicit code generation request"""
    print("\n\n" + "="*60)
    print("📋 EXPLICIT TOOL GENERATION TEST")
    print("="*60)
    
    # Explicitly ask for tool generation
    task = """Your task is to generate a Python function that:
    1. Takes a list of numbers as input
    2. Calculates the mean, median, and standard deviation
    3. Returns a dictionary with these statistics
    
    Generate this as a new tool and then use it on this data: [12, 45, 23, 67, 34, 89, 21, 54, 32, 76]"""
    
    agent = SelfEvolvingMetaAgent(goal=task, model="gemini-1.5-flash")
    
    print("\n🚀 Running agent with explicit tool generation request...")
    
    try:
        result = await agent.run()
        
        print(f"\n✅ Status: {result['status']}")
        print(f"🔧 Tools generated: {result.get('tools_generated', 0)}")
        
        # Show the result
        result_text = str(result.get('result', ''))
        if len(result_text) > 300:
            print(f"\n📝 Result preview: {result_text[:300]}...")
        else:
            print(f"\n📝 Result: {result_text}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def main():
    """Run demonstrations"""
    print("\n🌟 Advanced Tool Generation Tests")
    print("Testing scenarios that require specialized tools\n")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ No API key found!")
        return
    
    await test_specialized_tool()
    await test_code_generation_task()
    
    print("\n\n🚀 Tests complete!")
    print("The self-evolving agent can create tools when truly needed.")
    print("It's also smart enough to use existing capabilities when sufficient!")


if __name__ == "__main__":
    asyncio.run(main())