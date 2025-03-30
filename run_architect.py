"""
Architect - Autonomous AI Agent using browser-use with Gemini

To use with Gemini API:
1. Install the Google Gen AI SDK:
   pip install google-genai

2. Set up your API key in environment variables:
   export GEMINI_API_KEY="your-key-here"
   
   Or create a .env file with:
   GEMINI_API_KEY=your-key-here

NOTE ON BOT PROTECTION:
Many websites (especially sports sites like iplt20.com, espncricinfo.com, 
social media sites like Twitter/X, and news sites) use bot protection that 
can block automated browsers. Architect will first try to use browser 
automation, but will automatically fall back to direct Gemini queries if 
it detects that the browser is being blocked.
"""

import argparse
import asyncio
import json
from browser_use.architect.agents.architect_agent import ArchitectAgent
from browser_use.architect.agents.planner_agent import PlannerAgent

async def main(goal, show_plan_only=False):
    print(f"\n{'='*70}")
    print(f"Starting research on: {goal}")
    
    if show_plan_only:
        print(f"PLANNING MODE: Will only show the generated plan without execution")
        print(f"{'='*70}\n")
        
        # Create and run just the planner
        planner = PlannerAgent(goal=goal)
        plan = await planner.run()
        
        print(f"\nPLAN GENERATED:\n{'-'*70}")
        print(f"Generated {len(plan)} subtasks using {len(set(task['agent_type'] for task in plan))} different agent types:")
        
        for idx, task in enumerate(plan):
            print(f"\n[{idx+1}] {task['agent_type']}")
            print(f"Goal: {task['goal']}")
        
        print(f"\n{'='*70}")
        return plan
        
    else:
        print("Note: If target websites use bot protection, Architect will automatically")
        print("fall back to using Gemini's knowledge instead of browser automation.")
        print(f"{'='*70}\n")
        
        architect = ArchitectAgent(goal=goal)
        results = await architect.run()
        
        # Pretty print results from all agents
        print("\nFINAL RESULTS:\n" + ("="*70))
        
        if not results:
            print("No results were returned. There might have been an error.")
            return results
        
        for idx, result in enumerate(results):
            agent_name = result.get("agent", "Unknown")
            agent_goal = result.get("goal", "No goal specified")
            agent_result = result.get("result", "No result")
            
            print(f"\n[{idx+1}] {agent_name}")
            line_length = len(agent_name) + 5
            print(f"{'='*line_length}")
            print(f"Goal: {agent_goal}")
            print(f"Result: {'-'*65}")
            
            # Format the result for better readability
            if isinstance(agent_result, str):
                # Print the result with line wrapping
                print(agent_result)
            else:
                # If it's not a string, use JSON formatting
                try:
                    print(json.dumps(agent_result, indent=2))
                except:
                    print(str(agent_result))
            
            print(f"{'-'*70}")
        
        print(f"\n{'='*70}")
        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run The Architect")
    parser.add_argument("--goal", type=str, required=True, help="High-level goal")
    parser.add_argument("--show-plan-only", action="store_true", help="Only show the generated plan without executing it")
    args = parser.parse_args()
    asyncio.run(main(args.goal, args.show_plan_only))