#!/usr/bin/env python3
"""
Demonstration of the Self-Evolving MetaAgent

This example showcases how the agent can:
1. Identify missing capabilities
2. Generate new tools on the fly
3. Learn from failures and evolve tools
4. Build a growing library of capabilities

Try running this with different tasks to see how the agent adapts!
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from browser_use.architect.agents.self_evolving_meta_agent import SelfEvolvingMetaAgent
from browser_use.architect.agents.architect_agent import ArchitectAgent


async def demonstrate_self_evolution():
    """Demonstrate the self-evolving capabilities"""
    
    print("="*70)
    print("🧬 SELF-EVOLVING META AGENT DEMONSTRATION")
    print("="*70)
    print()
    
    # Example 1: Simple task that requires tool generation
    print("📋 Example 1: Analyzing CSV data (no built-in CSV tool)")
    print("-"*70)
    
    task1 = "Analyze this CSV data and find the top 3 values: Name,Score\\nAlice,95\\nBob,87\\nCarol,92\\nDave,88"
    
    agent1 = SelfEvolvingMetaAgent(goal=task1)
    result1 = await agent1.run()
    
    print(f"Result: {result1}")
    print(f"Tools generated: {result1.get('tools_generated', 0)}")
    print(f"New capabilities: {result1.get('capabilities_learned', [])}")
    print()
    
    # Example 2: Complex task requiring multiple tools
    print("📋 Example 2: Web scraping task (generates scraper tools)")
    print("-"*70)
    
    task2 = "Extract product prices from an e-commerce site and calculate the average"
    
    agent2 = SelfEvolvingMetaAgent(goal=task2)
    result2 = await agent2.run()
    
    print(f"Result: {result2}")
    print(f"Tools generated: {result2.get('tools_generated', 0)}")
    print()
    
    # Example 3: Using Architect with Self-Evolving agents
    print("📋 Example 3: Multi-agent collaboration with evolution")
    print("-"*70)
    
    architect_goal = "Research AI safety best practices and create a implementation checklist"
    
    # Modify the task to specifically use self-evolving agents
    architect = ArchitectAgent(goal=architect_goal)
    
    # This will use the planner to break down the task
    # The planner could assign "self-evolving" as the agent type for complex subtasks
    results = await architect.run()
    
    print("Architect Results:")
    for idx, result in enumerate(results):
        print(f"\n[{idx+1}] {result.get('agent', 'Unknown Agent')}")
        print(f"Goal: {result.get('goal', 'No goal')}")
        print(f"Status: {'✅ Success' if 'error' not in str(result.get('result', '')).lower() else '❌ Failed'}")
    
    print("\n" + "="*70)
    print("💡 KEY INSIGHTS:")
    print("="*70)
    print("1. The agent automatically identified missing capabilities")
    print("2. Generated safe, sandboxed tools to fill gaps")
    print("3. Tools can evolve based on performance")
    print("4. Each execution makes the system permanently smarter")
    print("5. No manual coding required for new capabilities!")


async def demonstrate_tool_evolution():
    """Show how tools evolve over multiple runs"""
    
    print("\n" + "="*70)
    print("🔄 TOOL EVOLUTION DEMONSTRATION")
    print("="*70)
    print()
    
    # Create an agent that will need to evolve its tools
    task = "Parse and validate email addresses from text, ensuring they follow RFC 5322 standards"
    
    agent = SelfEvolvingMetaAgent(goal=task)
    
    # Run multiple times to trigger evolution
    print("Running task 3 times to demonstrate evolution...")
    
    for i in range(3):
        print(f"\n--- Run {i+1} ---")
        result = await agent.run()
        
        if result["status"] == "success":
            print(f"✅ Success in {result.get('execution_time', 0):.2f}s")
            
            # Show tool performance
            for tool_name, perf_data in agent.tool_performance.items():
                if perf_data:
                    success_rate = sum(1 for p in perf_data if p["success"]) / len(perf_data)
                    print(f"   Tool '{tool_name}': {success_rate:.0%} success rate")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
    
    print("\n🎓 Tools evolved and improved through experience!")


async def main():
    """Run all demonstrations"""
    
    print("\n🚀 Welcome to the Self-Evolving MetaAgent Demo!\n")
    print("This demonstration shows how Architect can now:")
    print("- Generate its own tools when needed")
    print("- Learn from experience and evolve")
    print("- Solve problems it was never programmed for")
    print("\nLet's begin...\n")
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  Warning: No GEMINI_API_KEY found. Using mock mode.")
        print("   Set your API key for full functionality:")
        print("   export GEMINI_API_KEY='your-key-here'")
        print()
    
    try:
        # Run basic demonstration
        await demonstrate_self_evolution()
        
        # Run evolution demonstration
        await demonstrate_tool_evolution()
        
        print("\n✨ Demonstration complete!")
        print("\nTry modifying the tasks to see how the agent adapts to new challenges!")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        print("\nMake sure you have:")
        print("1. Set up your GEMINI_API_KEY environment variable")
        print("2. Installed all requirements: pip install -e .")


if __name__ == "__main__":
    asyncio.run(main())