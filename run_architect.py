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
from browser_use.architect.agents.architect_agent import ArchitectAgent

async def main(goal):
    print(f"Starting research on: {goal}")
    print("Note: If target websites use bot protection, Architect will automatically")
    print("fall back to using Gemini's knowledge instead of browser automation.")
    print("-" * 70)
    architect = ArchitectAgent(goal=goal)
    result = await architect.run()
    print("\nFINAL RESULT:\n" + ("-" * 50))
    print(result)
    print("-" * 50)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run The Architect")
    parser.add_argument("--goal", type=str, required=True, help="High-level goal")
    args = parser.parse_args()
    asyncio.run(main(args.goal))