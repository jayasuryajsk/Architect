import asyncio
import json
from browser_use.architect.agents.meta_agent import MetaAgent
from browser_use.architect.memory.memory_manager import log_message

async def test_meta_agent():
    print("\n" + "="*80)
    print("TESTING META AGENT")
    print("="*80 + "\n")
    
    # Specify a simple and clear goal
    goal = "Summarize benefits of open-source LLMs"
    agent_type = "ResearchSummarizer"
    
    print(f"Goal: {goal}")
    print(f"Agent Type: {agent_type}\n")
    
    # Create MetaAgent
    try:
        print("Creating MetaAgent...")
        meta_agent = MetaAgent(goal, "gemini-2.0-flash-lite", agent_type)
        
        print("\nRunning MetaAgent. This may take a minute...\n")
        
        # Define a simple callback to log progress
        async def callback(status, data):
            print(f"Status: {status}")
            if status == "processing":
                print(f"Progress: {data.get('message', 'No message')}")
            elif status == "error":
                print(f"Error: {data.get('error', 'Unknown error')}")
        
        # Run the agent with the callback
        result = await meta_agent.run(callback)
        
        print("\n" + "-"*40)
        print("RESULT:")
        print("-"*40 + "\n")
        
        if isinstance(result, str):
            print(result)
        else:
            try:
                # Try to pretty-print if it's JSON
                print(json.dumps(result, indent=2))
            except:
                print(result)
                
        print("\n" + "="*80)
        print("TEST COMPLETE")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        print(traceback.format_exc())
        print("\n" + "="*80)
        print("TEST FAILED")
        print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(test_meta_agent()) 