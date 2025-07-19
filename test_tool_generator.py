#!/usr/bin/env python3
"""Test the tool generator to see what's wrong"""

import asyncio
from browser_use.architect.core.tool_generator import AdvancedToolGenerator

async def test_generation():
    generator = AdvancedToolGenerator()
    
    # Test with a simple capability
    tool = await generator.generate_tool({
        'capability': 'count words in text',
        'context': 'text analysis'
    })
    
    if tool:
        print("Generated tool:")
        print("-" * 60)
        print(tool['code'])
        print("-" * 60)
        print(f"Validation passed: {tool.get('test_results', {}).get('success_rate', 0)}")
    else:
        print("Failed to generate tool")

if __name__ == "__main__":
    asyncio.run(test_generation())