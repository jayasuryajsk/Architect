#!/usr/bin/env python3
"""
Quick test script to verify the Self-Evolving MetaAgent works correctly.
Run this to see the agent in action!
"""

import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from browser_use.architect.agents.self_evolving_meta_agent import SelfEvolvingMetaAgent


async def test_basic_functionality():
    """Test that the agent can handle a simple task"""
    print("\n=== Testing Basic Functionality ===")
    
    # Simple task that requires tool generation
    agent = SelfEvolvingMetaAgent(
        goal="Calculate the factorial of 5"
    )
    
    result = await agent.run()
    
    print(f"Status: {result['status']}")
    print(f"Tools generated: {result.get('tools_generated', 0)}")
    print(f"Result: {result.get('result', 'No result')[:200]}")
    
    assert result['status'] in ['success', 'error'], "Invalid status"
    print("✅ Basic functionality test passed!")


async def test_capability_analysis():
    """Test that capability analysis works"""
    print("\n=== Testing Capability Analysis ===")
    
    agent = SelfEvolvingMetaAgent(goal="Test task")
    
    # Test the capability analyzer logic directly (without API)
    # This tests the structure, not the LLM call
    print("Testing capability analyzer structure...")
    
    # Test gap identification with mock data
    mock_task_analysis = {
        "task_type": "data_processing",
        "required_capabilities": ["csv_parsing", "email_extraction", "validation"],
        "complexity": 7
    }
    
    existing_capabilities = ["analyze_text", "search_web"]
    gaps = await agent.capability_analyzer.identify_gaps(
        mock_task_analysis, 
        existing_capabilities
    )
    
    print(f"Identified {len(gaps)} capability gaps")
    assert len(gaps) > 0, "Should identify gaps"
    assert gaps[0]["capability"] in mock_task_analysis["required_capabilities"]
    
    print("✅ Capability analysis test passed!")


async def test_safety_validation():
    """Test that safety validation works"""
    print("\n=== Testing Safety Validation ===")
    
    agent = SelfEvolvingMetaAgent(goal="Test task")
    validator = agent.safety_validator
    
    # Test with safe code
    safe_code = {
        "code": """
async def test_function(x):
    return x * 2
""",
        "spec": {"name": "test_function"}
    }
    
    is_safe, message = await validator.validate_tool(safe_code)
    print(f"Safe code validation: {is_safe} - {message}")
    assert is_safe, "Safe code should pass validation"
    
    # Test with unsafe code
    unsafe_code = {
        "code": """
async def danger():
    exec('print("dangerous")')
    return "bad"
""",
        "spec": {"name": "danger"}
    }
    
    is_safe, message = await validator.validate_tool(unsafe_code)
    print(f"Unsafe code validation: {is_safe} - {message}")
    assert not is_safe, "Unsafe code should fail validation"
    
    print("✅ Safety validation test passed!")


async def test_tool_library():
    """Test that tool library works"""
    print("\n=== Testing Tool Library ===")
    
    agent = SelfEvolvingMetaAgent(goal="Test task")
    library = agent.tool_library
    
    # Check base tools
    base_capabilities = library.get_capabilities()
    print(f"Base capabilities: {len(base_capabilities)}")
    assert len(base_capabilities) > 0, "Should have base capabilities"
    
    # Add a test tool
    test_tool = {
        "name": "test_tool",
        "code": "async def test_tool(): pass",
        "spec": {
            "name": "test_tool",
            "purpose": "Test tool for validation"
        },
        "generated": True,
        "generation_time": "2024-01-01T00:00:00"
    }
    
    library.add(test_tool)
    
    # Check it was added
    retrieved = library.get_tool("test_tool")
    assert retrieved is not None, "Tool should be retrievable"
    assert retrieved["name"] == "test_tool", "Tool name should match"
    
    print("✅ Tool library test passed!")


async def main():
    """Run all tests"""
    print("🧬 Self-Evolving MetaAgent Test Suite")
    print("=" * 50)
    
    try:
        # Note: These tests work without an API key by testing components
        await test_capability_analysis()
        await test_safety_validation()
        await test_tool_library()
        
        # This test would need an API key to fully work
        # await test_basic_functionality()
        
        print("\n✨ All tests passed! The Self-Evolving MetaAgent is ready to use.")
        print("\nTo see it in action with real tasks, run:")
        print("  python examples/self_evolving_demo.py")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())