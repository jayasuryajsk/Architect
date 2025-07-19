#!/usr/bin/env python3
"""
Real-world use case: Self-Evolving Research Assistant

This example shows how the Self-Evolving MetaAgent can tackle a complex
research task by generating specialized tools as needed.

The agent will:
1. Identify what tools it needs for the research
2. Generate scrapers, analyzers, and formatters
3. Evolve these tools based on what works
4. Produce a comprehensive research report
"""

import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent.parent))

from browser_use.architect.agents.architect_agent import ArchitectAgent
from browser_use.architect.agents.self_evolving_meta_agent import SelfEvolvingMetaAgent


async def research_with_evolution(topic: str):
    """
    Conduct research on a topic using self-evolving agents
    """
    print(f"\n{'='*80}")
    print(f"🔬 SELF-EVOLVING RESEARCH: {topic}")
    print(f"{'='*80}\n")
    
    # Create a research goal that will challenge the agent
    research_goal = f"""
    Conduct comprehensive research on: {topic}
    
    Requirements:
    1. Find the latest developments and trends
    2. Identify key players and organizations
    3. Analyze pros and cons
    4. Create a structured report with citations
    5. Generate actionable insights
    """
    
    print("📊 Phase 1: Initializing Self-Evolving Research Agent")
    print("-" * 80)
    
    start_time = datetime.now()
    
    # Use the self-evolving agent directly
    agent = SelfEvolvingMetaAgent(goal=research_goal)
    
    # Add callback to show progress
    async def progress_callback(event_type, data):
        if event_type == "tool_generated":
            print(f"  🔧 Generated new tool: {data['tool_name']}")
        elif event_type == "capability_gap":
            print(f"  🔍 Identified missing capability: {data['capability']}")
        elif event_type == "tool_evolved":
            print(f"  📈 Evolved tool: {data['tool_name']} (+{data['improvement']:.1%})")
    
    print("\n📊 Phase 2: Executing Research Task")
    print("-" * 80)
    
    result = await agent.run(callback=progress_callback)
    
    print("\n📊 Phase 3: Results")
    print("-" * 80)
    
    if result["status"] == "success":
        print(f"✅ Research completed successfully!")
        print(f"⏱️  Time taken: {(datetime.now() - start_time).total_seconds():.1f}s")
        print(f"🔧 Tools generated: {result.get('tools_generated', 0)}")
        print(f"🧠 New capabilities learned:")
        for capability in result.get('capabilities_learned', []):
            print(f"   - {capability}")
        
        print("\n📄 Research Output:")
        print("-" * 40)
        print(result["result"][:1000] + "..." if len(str(result["result"])) > 1000 else result["result"])
        
    else:
        print(f"❌ Research failed: {result.get('error', 'Unknown error')}")
    
    # Show tool library status
    print(f"\n📚 Tool Library Status:")
    print(f"   Active tools: {len(agent.tool_library.active_tools)}")
    print(f"   Base tools: {len(agent.tool_library.base_tools)}")
    print(f"   Total capabilities: {len(agent.tool_library.get_capabilities())}")
    
    return result


async def compare_with_traditional():
    """
    Compare self-evolving approach with traditional approach
    """
    print(f"\n{'='*80}")
    print("📊 COMPARISON: Self-Evolving vs Traditional Agents")
    print(f"{'='*80}\n")
    
    test_goal = "Analyze the environmental impact of electric vehicles vs hydrogen fuel cells"
    
    # Traditional approach
    print("🔹 Traditional Multi-Agent Approach:")
    print("-" * 40)
    
    traditional_start = datetime.now()
    architect = ArchitectAgent(goal=test_goal)
    traditional_results = await architect.run()
    traditional_time = (datetime.now() - traditional_start).total_seconds()
    
    print(f"✅ Completed in {traditional_time:.1f}s")
    print(f"📋 Agents used: {len(traditional_results)}")
    
    # Self-evolving approach
    print("\n🔹 Self-Evolving Approach:")
    print("-" * 40)
    
    evolving_start = datetime.now()
    evolving_agent = SelfEvolvingMetaAgent(goal=test_goal)
    evolving_result = await evolving_agent.run()
    evolving_time = (datetime.now() - evolving_start).total_seconds()
    
    print(f"✅ Completed in {evolving_time:.1f}s")
    print(f"🔧 Tools generated: {evolving_result.get('tools_generated', 0)}")
    print(f"🧠 Capabilities learned: {len(evolving_result.get('capabilities_learned', []))}")
    
    # Comparison
    print(f"\n📈 Performance Comparison:")
    print(f"   Time difference: {abs(traditional_time - evolving_time):.1f}s")
    print(f"   Adaptability: Self-evolving can handle unknown tasks")
    print(f"   Reusability: Generated tools persist for future use")


async def demonstrate_tool_reuse():
    """
    Show how generated tools are reused in subsequent tasks
    """
    print(f"\n{'='*80}")
    print("♻️  TOOL REUSE DEMONSTRATION")
    print(f"{'='*80}\n")
    
    # First task generates tools
    print("📋 Task 1: Cryptocurrency market analysis")
    agent = SelfEvolvingMetaAgent(goal="Analyze top 5 cryptocurrency trends and price movements")
    result1 = await agent.run()
    
    initial_tools = len(agent.tool_library.active_tools)
    print(f"✅ Generated {result1.get('tools_generated', 0)} new tools")
    
    # Second related task reuses tools
    print("\n📋 Task 2: NFT market analysis (reuses crypto analysis tools)")
    agent2 = SelfEvolvingMetaAgent(goal="Analyze NFT market trends and compare with cryptocurrency patterns")
    
    # Copy tool library (in practice, this would be persistent)
    agent2.tool_library = agent.tool_library
    
    result2 = await agent2.run()
    
    print(f"✅ Reused existing tools, generated {result2.get('tools_generated', 0)} additional tools")
    print(f"⚡ Efficiency gain from tool reuse!")
    
    # Show tool evolution
    print(f"\n📊 Tool Library Growth:")
    print(f"   After task 1: {initial_tools} tools")
    print(f"   After task 2: {len(agent2.tool_library.active_tools)} tools")
    print(f"   Tool reuse rate: {(1 - result2.get('tools_generated', 0)/max(1, initial_tools)) * 100:.0f}%")


async def main():
    """
    Run all demonstrations
    """
    print("\n🚀 SELF-EVOLVING RESEARCH ASSISTANT SHOWCASE")
    print("=" * 80)
    print("\nThis demonstration shows real-world applications of the Self-Evolving MetaAgent:")
    print("- Complex research tasks")
    print("- Tool generation and evolution") 
    print("- Performance comparisons")
    print("- Tool reuse and efficiency gains")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("\n⚠️  No GEMINI_API_KEY found. Set it for full functionality:")
        print("   export GEMINI_API_KEY='your-key-here'")
        return
    
    try:
        # Example 1: Research a complex topic
        await research_with_evolution("Quantum Computing applications in Drug Discovery")
        
        # Example 2: Compare approaches
        await compare_with_traditional()
        
        # Example 3: Demonstrate tool reuse
        await demonstrate_tool_reuse()
        
        print(f"\n{'='*80}")
        print("✨ DEMONSTRATION COMPLETE!")
        print(f"{'='*80}")
        print("\nKey Takeaways:")
        print("1. Self-evolving agents adapt to any research task")
        print("2. Generated tools improve over time through evolution")
        print("3. Tool libraries grow and become more valuable with use")
        print("4. No manual programming required for new capabilities")
        print("\n🚀 The future of autonomous AI is here!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())