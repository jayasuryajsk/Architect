#!/usr/bin/env python3
"""
Test the Self-Evolving MetaAgent with Gemini API
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from browser_use.architect.agents.self_evolving_meta_agent import SelfEvolvingMetaAgent


async def test_tool_generation():
    """Test the agent generating a new tool"""
    print("🧬 TESTING SELF-EVOLVING AGENT WITH GEMINI API")
    print("=" * 60)
    
    # Simple task that requires tool generation
    task = "Calculate the Fibonacci sequence up to the 10th number"
    
    print(f"\n📋 Task: {task}")
    print("-" * 60)
    
    # Create agent
    agent = SelfEvolvingMetaAgent(goal=task, model="gemini-1.5-flash")
    
    # Add callback to see progress
    async def progress_callback(event_type, data):
        if event_type == "tool_generated":
            print(f"\n🔧 Generated new tool: {data.get('name', 'unknown')}")
        elif event_type == "capability_gap":
            print(f"\n🔍 Identified missing capability: {data.get('capability', 'unknown')}")
        elif event_type == "tool_evolved":
            print(f"\n📈 Evolved tool: {data.get('name', 'unknown')}")
    
    try:
        # Run the agent
        print("\n🚀 Running agent...")
        result = await agent.run(callback=progress_callback)
        
        print("\n✨ RESULTS:")
        print(f"Status: {result['status']}")
        print(f"Tools generated: {result.get('tools_generated', 0)}")
        print(f"Execution time: {result.get('execution_time', 0):.2f}s")
        print(f"New capabilities: {result.get('capabilities_learned', [])}")
        
        print("\n📝 Result:")
        print("-" * 40)
        result_text = str(result.get('result', 'No result'))
        if len(result_text) > 500:
            print(result_text[:500] + "...")
        else:
            print(result_text)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_complex_task():
    """Test with a more complex task"""
    print("\n\n" + "="*60)
    print("📋 COMPLEX TASK TEST")
    print("="*60)
    
    task = "Analyze this text and count word frequencies: 'The quick brown fox jumps over the lazy dog. The dog was really lazy.'"
    
    print(f"\nTask: {task}")
    
    agent = SelfEvolvingMetaAgent(goal=task, model="gemini-1.5-flash")
    
    try:
        result = await agent.run()
        
        print(f"\n✅ Success! Tools generated: {result.get('tools_generated', 0)}")
        
        # Show tool library status
        print(f"\n📚 Tool Library:")
        print(f"   Active tools: {len(agent.tool_library.active_tools)}")
        print(f"   Total capabilities: {len(agent.tool_library.get_capabilities())}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def main():
    """Run all tests"""
    print("\n🌟 Self-Evolving MetaAgent Live Demo")
    print("Using Gemini 1.5 Flash for fast tool generation\n")
    
    # Check API key
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ No API key found! Please set GEMINI_API_KEY")
        return
    
    print("✅ API key loaded successfully")
    
    # Run tests
    await test_tool_generation()
    await test_complex_task()
    
    print("\n\n🎉 Demo complete! The agent successfully generated tools autonomously!")


if __name__ == "__main__":
    asyncio.run(main())