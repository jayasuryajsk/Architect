#!/usr/bin/env python
"""
SummarizerAgent Example - Demonstrates using the SummarizerAgent to summarize multiple results

This example shows how to use the SummarizerAgent directly to summarize results from multiple sources.

Usage:
    python examples/summarizer_example.py

Requirements:
    - Set GEMINI_API_KEY in .env or as environment variable
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from browser_use.architect.agents.summarizer_agent import SummarizerAgent
from browser_use.architect.memory.memory_manager import log_message

# Load environment variables
load_dotenv()

async def run_example():
    """Run an example of the SummarizerAgent."""
    # Check if API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️ GEMINI_API_KEY not found. Please set it in .env file or environment.")
        return
    
    # Define a goal for summarization
    goal = "Summarize information about popular AI frameworks"
    
    # Create sample results (in a real scenario, these would come from other agents)
    mock_results = [
        {
            "subtask": "Research TensorFlow framework",
            "agent_type": "Researcher",
            "result": "TensorFlow is an open-source machine learning framework developed by Google. "
                      "It provides a comprehensive ecosystem of tools, libraries, and resources for "
                      "building and deploying machine learning models. TensorFlow is known for its "
                      "flexibility, scalability, and support for deep learning applications.",
            "task_id": "task-001"
        },
        {
            "subtask": "Research PyTorch framework",
            "agent_type": "Researcher",
            "result": "PyTorch is an open-source machine learning library developed by Facebook's "
                      "AI Research lab. It's known for its dynamic computational graph, which makes "
                      "it more intuitive for developers familiar with Python. PyTorch has gained "
                      "significant popularity in research settings due to its flexibility and ease of debugging.",
            "task_id": "task-002"
        },
        {
            "subtask": "Evaluate framework performance",
            "agent_type": "Critic",
            "result": "When comparing TensorFlow and PyTorch: TensorFlow excels in production environments "
                      "with TensorFlow Serving and has better support for mobile deployment. PyTorch offers "
                      "a more Pythonic experience with dynamic computation graphs making development and "
                      "debugging more intuitive. Both frameworks have strong community support and extensive "
                      "documentation.",
            "task_id": "task-003"
        }
    ]
    
    print("=" * 80)
    print(f"🎯 GOAL: {goal}")
    print("=" * 80)
    
    print("\nIndividual Results:")
    for i, result in enumerate(mock_results):
        print(f"\n{i+1}. [{result['agent_type']}] {result['subtask']}")
        print("-" * 40)
        print(result['result'])
    
    print("\n" + "=" * 80)
    print("🚀 Running SummarizerAgent...")
    
    # Create and run the SummarizerAgent
    summarizer = SummarizerAgent(
        goal=goal,
        results=mock_results,
        model="gemini-2.0-flash-lite"
    )
    
    # Run the summarizer and get the final summary
    summary = await summarizer.run()
    
    print("\n" + "=" * 80)
    print("📋 FINAL SUMMARY:")
    print("=" * 80)
    print(summary)
    print("=" * 80)
    
    return summary

if __name__ == "__main__":
    asyncio.run(run_example()) 