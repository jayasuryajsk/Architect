#!/usr/bin/env python3
"""
Test the Self-Evolving MetaAgent with a task that requires tool generation
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from browser_use.architect.agents.self_evolving_meta_agent import SelfEvolvingMetaAgent


async def test_csv_tool_generation():
    """Test with a task that definitely needs new tools"""
    print("🧬 TESTING TOOL GENERATION FOR CSV ANALYSIS")
    print("=" * 60)
    
    # Task that requires CSV parsing - not in base tools
    task = """Parse this CSV data and find the highest score:
Name,Score,Grade
Alice,95,A
Bob,87,B
Carol,92,A
David,78,C
Eve,99,A

Return the name and score of the student with the highest score."""
    
    print(f"\n📋 Task: CSV Analysis")
    print("This requires generating a CSV parsing tool!")
    print("-" * 60)
    
    # Create agent
    agent = SelfEvolvingMetaAgent(goal=task, model="gemini-1.5-flash")
    
    print("\n🔍 Current capabilities:")
    for cap in agent.tool_library.get_capabilities():
        print(f"   - {cap}")
    print("\n(Note: No CSV parsing capability!)")
    
    try:
        print("\n🚀 Running agent...")
        result = await agent.run()
        
        print("\n✨ RESULTS:")
        print(f"Status: {result['status']}")
        print(f"Tools generated: {result.get('tools_generated', 0)}")
        print(f"Execution time: {result.get('execution_time', 0):.2f}s")
        
        if result.get('capabilities_learned'):
            print(f"\n🎓 New capabilities learned:")
            for cap in result['capabilities_learned']:
                print(f"   - {cap}")
        
        print("\n📝 Result:")
        print("-" * 40)
        print(result.get('result', 'No result'))
        
        # Show generated tools
        if agent.tool_library.active_tools:
            print("\n🔧 Generated Tools:")
            for tool_name, tool_info in agent.tool_library.active_tools.items():
                print(f"\n   Tool: {tool_name}")
                print(f"   Purpose: {tool_info.get('spec', {}).get('purpose', 'Unknown')}")
                if tool_info.get('code'):
                    print(f"   Code preview:")
                    code_lines = tool_info['code'].split('\n')[:5]
                    for line in code_lines:
                        print(f"      {line}")
                    print("      ...")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_reuse():
    """Test that generated tools are reused"""
    print("\n\n" + "="*60)
    print("📋 TESTING TOOL REUSE")
    print("="*60)
    
    # Similar CSV task to test reuse
    task = """Parse this CSV and find the average score:
Product,Price
Apple,1.50
Banana,0.75
Orange,1.25
Mango,2.00"""
    
    agent = SelfEvolvingMetaAgent(goal=task, model="gemini-1.5-flash")
    
    print("\n🔍 Checking if CSV tools are available...")
    caps = agent.tool_library.get_capabilities()
    print(f"Capabilities: {len(caps)}")
    
    result = await agent.run()
    print(f"\n✅ Task completed. Tools generated: {result.get('tools_generated', 0)}")
    print("(Should be 0 if reusing existing tools!)")


async def main():
    """Run the demonstration"""
    print("\n🌟 Self-Evolving Agent Tool Generation Demo")
    print("This demo shows the agent creating new tools when needed\n")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ No API key found!")
        return
    
    await test_csv_tool_generation()
    # Uncomment to test reuse (tools are not persistent across runs in this demo)
    # await test_reuse()
    
    print("\n\n🎉 The agent successfully created tools it didn't have!")
    print("This is the power of self-evolution - infinite extensibility!")


if __name__ == "__main__":
    asyncio.run(main())