#!/usr/bin/env python3
import argparse
import asyncio
import json
import sys
from typing import Dict, Any, List, Union

from browser_use.architect.agents.architect_agent import ArchitectAgent
from browser_use.architect.agents.critic_agent import CriticAgent

async def print_status(status: str, data: Dict[str, Any]):
    """
    Print status updates from the agents.
    
    Args:
        status: The status type
        data: The status data
    """
    if status == "planning":
        print(f"⚙️  Creating multi-agent plan...")
    elif status == "plan_created":
        print(f"✅ Created plan with {data.get('subtasks', 0)} subtasks")
    elif status == "spawn_agent":
        agent_type = data.get('agent_type', 'Unknown')
        goal = data.get('goal', 'Unknown')
        index = data.get('index', 0)
        print(f"🔄 Starting {agent_type} agent #{index}: {goal[:60] + '...' if len(goal) > 60 else goal}")
    elif status == "agent_complete":
        agent = data.get('agent', 'Unknown')
        print(f"✅ {agent} finished")
    elif status == "error":
        print(f"❌ Error: {data.get('error', 'Unknown error')}")
    elif status == "fallback_plan":
        print(f"⚠️  Using fallback plan due to error: {data.get('error', 'Unknown error')}")

def extract_refined_goal(goal_critic_output: Union[str, Dict[str, Any]], original_goal: str) -> str:
    """
    Extract the refined goal text from the critic output.
    
    Args:
        goal_critic_output: The output from the critic agent
        original_goal: The original user goal to fall back to
        
    Returns:
        The refined goal as a string
    """
    if isinstance(goal_critic_output, dict):
        # Check for error status
        if goal_critic_output.get("status") == "error":
            print(f"⚠️ Goal refinement failed: {goal_critic_output.get('error', 'Unknown error')}")
            return original_goal
            
        # New format with 'refined' field
        if "refined" in goal_critic_output:
            refined = goal_critic_output["refined"]
            notes = goal_critic_output.get("notes", "No explanation provided")
            print(f"📝 Refinement notes: {notes}")
            return refined
            
        # Fallback to other possible keys
        for key in ["text", "result"]:
            if key in goal_critic_output:
                return goal_critic_output[key]
                
        # If no valid keys found, return original
        return original_goal
    
    # If output is already a string, return it
    if isinstance(goal_critic_output, str):
        return goal_critic_output
        
    # Otherwise convert to string
    return str(goal_critic_output)

async def run_with_goal_refinement(goal: str):
    """
    Run the architect with goal refinement first.
    
    Args:
        goal: The user's original goal
    """
    print("\n" + "="*70)
    print(f"Starting Enhanced Architect workflow")
    print("="*70 + "\n")
    
    print(f"📌 Original goal: {goal}")
    
    # Step 1: Refine the goal using the CriticAgent
    try:
        print("\n🔍 Refining goal with CriticAgent...")
        critic = CriticAgent(goal=goal)
        goal_critic_output = await critic.refine_goal()
        
        # Extract the refined goal using the helper function
        refined_goal = extract_refined_goal(goal_critic_output, goal)
        
        if refined_goal != goal:
            print(f"✅ Goal refined: {refined_goal}")
        else:
            print("⚠️ Goal refinement didn't yield improvements")
    except Exception as e:
        print(f"❌ Goal refinement failed: {e}")
        refined_goal = goal
    
    # Step 2: Run the architect with the refined goal
    print("\n🚀 Running Architect with refined goal...\n")
    
    architect = ArchitectAgent(goal=refined_goal)
    results = await architect.run(callback=print_status)
    
    # Step 3: Output the results
    print("\nFINAL RESULTS:")
    print("="*70)
    print()
    
    for idx, result in enumerate(results):
        agent = result.get("agent", "Unknown")
        goal = result.get("goal", "Unknown")
        response = result.get("result", "No result")
        
        print(f"[{idx+1}] {agent}")
        print("="*len(agent) + "=" * (len(str(idx+1)) + 3))
        print(f"Goal: {goal}")
        
        print("Result: " + "-"*65)
        if isinstance(response, str):
            print(response)
        else:
            try:
                # Try to pretty print if JSON
                print(json.dumps(response, indent=2))
            except:
                print(str(response))
        print("-"*70)
        print()
    
    print("="*70)
    print()

def main():
    """Parse arguments and run the architect."""
    parser = argparse.ArgumentParser(description="Run Architect with goal refinement")
    parser.add_argument("--goal", type=str, required=True, help="High-level goal to achieve")
    
    args = parser.parse_args()
    
    if not args.goal:
        print("Error: Goal is required")
        return 1
    
    try:
        asyncio.run(run_with_goal_refinement(args.goal))
        return 0
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 