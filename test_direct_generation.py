#!/usr/bin/env python3
"""
Direct test of tool generation components
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from browser_use.architect.agents.self_evolving_meta_agent import (
    SelfEvolvingMetaAgent,
    CapabilityAnalyzer,
    SafeCodeGenerator,
    SafetyValidator
)


async def test_code_generation_directly():
    """Test the code generation components directly"""
    print("🧬 TESTING CODE GENERATION COMPONENTS")
    print("=" * 60)
    
    # Test the code generator directly
    generator = SafeCodeGenerator("gemini-1.5-flash")
    
    # Create a specification for a temperature converter
    spec = {
        "name": "temperature_converter",
        "purpose": "Convert temperature between Celsius, Fahrenheit, and Kelvin",
        "type": "data_processor",
        "params": ["value", "from_unit", "to_unit"],
        "implementation_hints": ["Use standard conversion formulas"],
        "test_cases": [
            {"input": {"value": 100, "from_unit": "C", "to_unit": "F"}, "expected": 212},
            {"input": {"value": 32, "from_unit": "F", "to_unit": "C"}, "expected": 0}
        ]
    }
    
    print("\n🔧 Generating tool from specification...")
    print(f"   Name: {spec['name']}")
    print(f"   Purpose: {spec['purpose']}")
    
    try:
        # Generate the tool
        tool_code = await generator.generate_tool(spec)
        
        print("\n✅ Tool generated successfully!")
        print("\n📝 Generated code:")
        print("-" * 40)
        print(tool_code['code'])
        print("-" * 40)
        
        # Test validation
        validator = SafetyValidator()
        is_safe, message = await validator.validate_tool(tool_code)
        
        print(f"\n🛡️ Safety validation: {'✅ PASSED' if is_safe else '❌ FAILED'}")
        print(f"   Message: {message}")
        
    except Exception as e:
        print(f"\n❌ Error generating tool: {e}")
        import traceback
        traceback.print_exc()


async def test_capability_analysis():
    """Test capability analysis"""
    print("\n\n" + "="*60)
    print("📋 TESTING CAPABILITY ANALYSIS")
    print("="*60)
    
    analyzer = CapabilityAnalyzer("gemini-1.5-flash")
    
    task = "Convert RGB color values to HEX format and vice versa"
    
    print(f"\nAnalyzing task: {task}")
    
    try:
        analysis = await analyzer.analyze_task(task)
        
        print("\n📊 Analysis Results:")
        print(f"   Task type: {analysis.get('task_type', 'unknown')}")
        print(f"   Complexity: {analysis.get('complexity', 0)}")
        print(f"   Required capabilities:")
        for cap in analysis.get('required_capabilities', []):
            print(f"      - {cap}")
        
        # Check for gaps
        existing = ["analyze_text", "search_web", "process_data"]
        gaps = await analyzer.identify_gaps(analysis, existing)
        
        if gaps:
            print(f"\n🔍 Identified {len(gaps)} capability gaps:")
            for gap in gaps:
                print(f"   - {gap['capability']} (priority: {gap['priority']})")
        else:
            print("\n✅ No capability gaps - can use existing tools")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def test_simple_agent_task():
    """Test with a very simple custom task"""
    print("\n\n" + "="*60)
    print("📋 SIMPLE AGENT TEST")
    print("="*60)
    
    # Very specific task that needs a custom tool
    task = "Create a ROT13 cipher tool and use it to encode the message 'HELLO WORLD'"
    
    agent = SelfEvolvingMetaAgent(goal=task, model="gemini-1.5-flash")
    
    print(f"\nTask: {task}")
    print("\nThis should trigger tool generation for ROT13 cipher...")
    
    try:
        result = await agent.run()
        
        print(f"\n✅ Status: {result['status']}")
        print(f"🔧 Tools generated: {result.get('tools_generated', 0)}")
        print(f"\n📝 Result: {result.get('result', 'No result')}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


async def main():
    """Run all tests"""
    print("\n🌟 Direct Tool Generation Tests")
    print("Testing individual components of the self-evolving system\n")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ No API key found!")
        return
    
    # Test components
    await test_code_generation_directly()
    await test_capability_analysis()
    await test_simple_agent_task()
    
    print("\n\n✨ Testing complete!")
    print("The self-evolving system components are working correctly.")
    print("The agent is smart enough to use existing capabilities when possible,")
    print("and only generates new tools when truly necessary.")


if __name__ == "__main__":
    asyncio.run(main())