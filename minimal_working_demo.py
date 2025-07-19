#!/usr/bin/env python3
"""Minimal working demo that actually shows the agent capabilities"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Direct approach - use the web tools directly
from browser_use.architect.core.web_tools import search_web_tool, compare_housing_markets

async def demo_web_search():
    """Demo real web search"""
    print("\n🔍 DEMO: Web Search")
    print("="*60)
    
    result = await search_web_tool("Python programming tutorials 2024", num_results=5)
    
    print("\nSearch Results:")
    for i, item in enumerate(result['result'], 1):
        print(f"\n{i}. {item['title']}")
        print(f"   URL: {item['url']}")
        print(f"   Snippet: {item['snippet'][:100]}...")

async def demo_housing_comparison():
    """Demo housing market comparison"""
    print("\n🏠 DEMO: Housing Market Comparison")
    print("="*60)
    
    result = await compare_housing_markets("Sydney", "Canberra")
    
    print("\nComparison Summary:")
    print(f"Locations: {result['result']['locations']}")
    print(f"Total sources found: {result['metadata']['total_sources']}")
    
    # Show some data
    for location, data in result['result']['data'].items():
        print(f"\n{location}:")
        print(f"  Sources: {len(data['sources'])}")
        if data['sources']:
            print(f"  Sample source: {data['sources'][0]['title']}")

async def main():
    print("\n🚀 ARCHITECT V2 - WORKING DEMOS")
    print("="*80)
    print("\nThese demos show the actual capabilities without the complex generation overhead\n")
    
    # Check API key
    if not os.getenv('GEMINI_API_KEY'):
        print("❌ Please set GEMINI_API_KEY environment variable")
        return
    
    try:
        # Run web search demo
        await demo_web_search()
        
        print("\n" + "-"*60)
        
        # Run housing comparison demo
        await demo_housing_comparison()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())