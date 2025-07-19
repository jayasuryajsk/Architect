#!/usr/bin/env python3
"""
SOTA Self-Evolving Agent Demo
Shows the new capabilities of the redesigned system
"""

import asyncio
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()

from browser_use.architect.agents.self_evolving_agent_v2 import SelfEvolvingAgentV2


async def demo_housing_market_comparison():
    """Demo: Compare housing markets with real data"""
    print("\n" + "="*80)
    print("🏠 DEMO: Real Estate Market Comparison")
    print("="*80)
    
    agent = SelfEvolvingAgentV2()
    
    task = "Compare the housing markets of Sydney and Canberra with real current data"
    
    result = await agent.run(task, max_duration_hours=0.5)  # 30 minutes max
    
    print("\n📊 RESULT:")
    print("-"*80)
    if result.get('success'):
        print(result['result'])
        print(f"\n⏱️ Execution time: {result['execution_time']:.1f} seconds")
        print(f"🔧 Tools used: {', '.join(result['tools_used'])}")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    # Show agent status
    status = await agent.get_status()
    print(f"\n📈 Agent Status:")
    print(f"   Tools available: {status['tools_available']}")
    print(f"   Tools generated: {status['tools_generated']}")


async def demo_complex_research():
    """Demo: Complex multi-step research task"""
    print("\n" + "="*80)
    print("🔬 DEMO: Complex Research Task")
    print("="*80)
    
    agent = SelfEvolvingAgentV2()
    
    task = """
    Research and analyze:
    1. Current AI agent architectures and their limitations
    2. Self-modifying code techniques and safety measures
    3. Compare top 3 autonomous agent frameworks
    4. Synthesize findings into actionable improvements
    """
    
    result = await agent.run(task, max_duration_hours=1.0)
    
    print("\n📊 RESULT:")
    print("-"*80)
    if result.get('success'):
        print(result['result'])
    else:
        print(f"❌ Error: {result.get('error')}")


async def demo_tool_generation():
    """Demo: Generate specialized tools on demand"""
    print("\n" + "="*80)
    print("🔧 DEMO: Dynamic Tool Generation")
    print("="*80)
    
    agent = SelfEvolvingAgentV2()
    
    task = "Create a tool to analyze Python code complexity and suggest improvements"
    
    result = await agent.run(task, max_duration_hours=0.25)
    
    print("\n📊 RESULT:")
    print("-"*80)
    if result.get('success'):
        print(result['result'])
        print(f"\n🔧 New tools generated: {agent.tools_generated}")
    else:
        print(f"❌ Error: {result.get('error')}")


async def demo_continuous_operation():
    """Demo: Long-running autonomous operation"""
    print("\n" + "="*80)
    print("♾️ DEMO: Continuous Autonomous Operation")
    print("="*80)
    
    agent = SelfEvolvingAgentV2()
    
    # Start autonomous evolution in background
    evolution_task = asyncio.create_task(
        agent.evolve_autonomously(duration_hours=0.1)  # 6 minutes for demo
    )
    
    # Run multiple tasks
    tasks = [
        "Find the latest news about autonomous AI agents",
        "Analyze trends in machine learning frameworks",
        "Compare cloud computing providers for ML workloads"
    ]
    
    for task in tasks:
        print(f"\n🎯 Running: {task}")
        result = await agent.run(task, max_duration_hours=0.1)
        
        if result.get('success'):
            print(f"✅ Completed in {result['execution_time']:.1f}s")
        else:
            print(f"❌ Failed: {result.get('error')}")
        
        # Show progress
        status = await agent.get_status()
        print(f"   Total tasks completed: {status['tasks_completed']}")
        print(f"   Tools available: {status['tools_available']}")
    
    # Cancel evolution
    evolution_task.cancel()
    
    print("\n✅ Continuous operation demo complete")


async def interactive_demo():
    """Interactive demo where user can input tasks"""
    print("\n" + "="*80)
    print("🎮 INTERACTIVE DEMO - SOTA Self-Evolving Agent")
    print("="*80)
    print("\nThis agent can:")
    print("  • Generate its own tools")
    print("  • Access real web data")
    print("  • Learn from experience")
    print("  • Run tasks in parallel")
    print("  • Operate autonomously for hours")
    
    agent = SelfEvolvingAgentV2()
    
    while True:
        print("\n" + "-"*60)
        task = input("Enter your task (or 'quit' to exit): ").strip()
        
        if task.lower() in ['quit', 'exit', 'q']:
            break
            
        if not task:
            continue
        
        print(f"\n⏳ Processing: {task}")
        
        try:
            result = await agent.run(task, max_duration_hours=0.5)
            
            print("\n📊 RESULT:")
            print("-"*60)
            if result.get('success'):
                print(result['result'])
                print(f"\n⏱️ Time: {result['execution_time']:.1f}s")
                print(f"🔧 Tools: {', '.join(result['tools_used'])}")
            else:
                print(f"❌ Error: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        # Show status
        status = await agent.get_status()
        print(f"\n📈 Session Stats:")
        print(f"   Uptime: {status['uptime_hours']:.2f} hours")
        print(f"   Tasks completed: {status['tasks_completed']}")
        print(f"   Tools generated: {status['tools_generated']}")
        print(f"   Tools available: {status['tools_available']}")
    
    print("\n👋 Thanks for trying the SOTA agent!")


async def main():
    """Run all demos"""
    
    print("\n🚀 SOTA SELF-EVOLVING AGENT V2 DEMOS")
    print("="*80)
    
    demos = [
        ("Housing Market Comparison", demo_housing_market_comparison),
        ("Complex Research", demo_complex_research),
        ("Tool Generation", demo_tool_generation),
        ("Continuous Operation", demo_continuous_operation),
        ("Interactive Mode", interactive_demo)
    ]
    
    print("\nAvailable demos:")
    for i, (name, _) in enumerate(demos, 1):
        print(f"  {i}. {name}")
    print(f"  {len(demos)+1}. Run all demos")
    print("  q. Quit")
    
    while True:
        choice = input("\nSelect demo (1-6 or q): ").strip().lower()
        
        if choice == 'q':
            break
        elif choice == str(len(demos)+1):
            # Run all demos
            for name, demo_func in demos[:-1]:  # Skip interactive
                print(f"\n{'='*80}")
                print(f"Running: {name}")
                print('='*80)
                await demo_func()
                input("\nPress Enter to continue...")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(demos):
                    await demos[idx][1]()
                else:
                    print("Invalid choice")
            except ValueError:
                print("Invalid input")
    
    print("\n✅ Demo complete!")


if __name__ == "__main__":
    asyncio.run(main())