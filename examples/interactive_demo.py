#!/usr/bin/env python3
"""
Interactive demo - Try any task with the Self-Evolving MetaAgent!
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from browser_use.architect.agents.self_evolving_meta_agent import SelfEvolvingMetaAgent


async def run_custom_task(task: str):
    """Run any custom task"""
    print("\n" + "="*70)
    print("🚀 RUNNING YOUR TASK")
    print("="*70)
    print(f"\nTask: {task}")
    print("\n⏳ Processing... (this may take a moment)")
    
    agent = SelfEvolvingMetaAgent(goal=task)
    
    # Track progress
    async def progress_callback(event_type, data):
        if event_type == "capability_gap":
            print(f"   🔍 Identified need for: {data.get('capability', 'unknown')}")
        elif event_type == "tool_generated":
            print(f"   🔧 Generated tool: {data.get('name', 'unknown')}")
        elif event_type == "analyzing":
            print(f"   🔍 {data.get('message', 'Analyzing...')}")
        elif event_type == "executing":
            print(f"   ⚡ {data.get('message', 'Executing...')}")
        else:
            print(f"   📌 {event_type}: {data}")
    
    try:
        print("\n   📊 Starting analysis...")
        result = await agent.run(callback=progress_callback)
        
        print(f"\n✅ Status: {result['status']}")
        print(f"🔧 Tools generated: {result.get('tools_generated', 0)}")
        
        if result.get('capabilities_learned'):
            print("\n🎓 New capabilities learned:")
            for cap in result['capabilities_learned']:
                print(f"   - {cap}")
        
        print("\n📝 Result:")
        print("-" * 50)
        print(result.get('result', 'No result'))
        print("-" * 50)
        
        # Show tool library status
        print(f"\n📚 Tool Library Status:")
        print(f"   Total tools: {len(agent.tool_library.active_tools) + len(agent.tool_library.base_tools)}")
        
        if agent.tool_library.active_tools:
            print("\n🔧 Generated tools available for future use:")
            for tool_name in agent.tool_library.active_tools:
                print(f"   - {tool_name}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Interactive demo"""
    print("\n🌟 SELF-EVOLVING AGENT - INTERACTIVE DEMO")
    print("="*70)
    print("\nThis agent can create any tools it needs to complete your task!")
    print("It will analyze what's needed, generate safe code, and execute it.\n")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ No API key found! Please set GEMINI_API_KEY")
        return
    
    print("💡 Example tasks you can try:")
    print("   - 'Convert this text to Morse code: HELLO WORLD'")
    print("   - 'Calculate compound interest on $1000 at 5% for 10 years'")
    print("   - 'Generate a simple ASCII art of a smiley face'")
    print("   - 'Create a tool to validate email addresses'")
    print("   - 'Analyze word frequency in a paragraph'")
    print("   - Or anything else you can imagine!\n")
    
    while True:
        try:
            print("\n" + "-"*70)
            task = input("\n🎯 Enter your task (or 'quit' to exit):\n> ").strip()
            
            if task.lower() in ['quit', 'exit', 'q']:
                break
            
            if not task:
                print("Please enter a task!")
                continue
            
            await run_custom_task(task)
            
            print("\n✨ Task complete! The agent handled it by:")
            print("   1. Analyzing what capabilities were needed")
            print("   2. Generating any missing tools")
            print("   3. Validating the code for safety")
            print("   4. Executing the solution")
            
            again = input("\n🔄 Try another task? (y/n): ").strip().lower()
            if again != 'y':
                break
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
    
    print("\n\n🎉 Thanks for trying the Self-Evolving MetaAgent!")
    print("This is the future of AI - agents that adapt to any task!")


if __name__ == "__main__":
    asyncio.run(main())