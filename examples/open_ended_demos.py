#!/usr/bin/env python3
"""
Open-ended examples to demonstrate the Self-Evolving MetaAgent's capabilities
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from browser_use.architect.agents.self_evolving_meta_agent import SelfEvolvingMetaAgent


async def example_data_analysis():
    """Data analysis task requiring custom tools"""
    print("\n" + "="*70)
    print("📊 EXAMPLE 1: Data Analysis")
    print("="*70)
    
    task = """
    I have this sales data:
    
    Product,Q1,Q2,Q3,Q4
    Laptops,150,220,180,310
    Phones,450,520,490,680
    Tablets,80,95,110,125
    Watches,200,210,195,240
    
    Please:
    1. Calculate the total annual sales for each product
    2. Find which product had the highest growth from Q1 to Q4
    3. Calculate the average quarterly sales across all products
    4. Identify any seasonal trends
    """
    
    agent = SelfEvolvingMetaAgent(goal=task)
    result = await agent.run()
    
    print(f"\n✅ Status: {result['status']}")
    print(f"🔧 Tools generated: {result.get('tools_generated', 0)}")
    print(f"\n📝 Result:\n{result.get('result', 'No result')}")


async def example_text_processing():
    """Text processing requiring custom analysis"""
    print("\n" + "="*70)
    print("📝 EXAMPLE 2: Text Processing")
    print("="*70)
    
    task = """
    Analyze this customer feedback and:
    1. Extract the main sentiment (positive/negative/neutral)
    2. Identify the top 3 most mentioned issues
    3. Count how many times each product feature is mentioned
    
    Feedback:
    "The laptop is fast but the battery life is terrible. Screen quality is amazing though."
    "Love the new phone camera! Battery lasts all day. Wish it had wireless charging."
    "Tablet is perfect for reading. Screen could be brighter. Great battery life!"
    "The smartwatch fitness tracking is accurate but the battery dies too quickly."
    "Phone screen is beautiful. Camera is okay. Really miss having a headphone jack."
    """
    
    agent = SelfEvolvingMetaAgent(goal=task)
    result = await agent.run()
    
    print(f"\n✅ Status: {result['status']}")
    print(f"🔧 Tools generated: {result.get('tools_generated', 0)}")
    print(f"\n📝 Analysis:\n{result.get('result', 'No result')}")


async def example_code_generation():
    """Ask it to create something specific"""
    print("\n" + "="*70)
    print("💻 EXAMPLE 3: Code Generation")
    print("="*70)
    
    task = """
    Create a password strength checker that:
    1. Checks if password is at least 8 characters
    2. Has at least one uppercase letter
    3. Has at least one lowercase letter
    4. Has at least one number
    5. Has at least one special character
    6. Returns a strength score from 0-100
    
    Then test it with these passwords:
    - "password123"
    - "P@ssw0rd!"
    - "abc"
    - "MyStr0ng!Pass#2024"
    """
    
    agent = SelfEvolvingMetaAgent(goal=task)
    result = await agent.run()
    
    print(f"\n✅ Status: {result['status']}")
    print(f"🔧 Tools generated: {result.get('tools_generated', 0)}")
    print(f"\n📝 Result:\n{result.get('result', 'No result')}")


async def example_math_problem():
    """Mathematical computation"""
    print("\n" + "="*70)
    print("🔢 EXAMPLE 4: Mathematical Analysis")
    print("="*70)
    
    task = """
    I need to analyze these test scores and calculate:
    1. The mean, median, and mode
    2. Standard deviation
    3. How many students scored above 80%
    4. The grade distribution (A: 90-100, B: 80-89, C: 70-79, D: 60-69, F: <60)
    
    Scores: 85, 92, 78, 95, 88, 73, 91, 84, 79, 96, 82, 87, 90, 76, 93, 89, 77, 94, 86, 81
    """
    
    agent = SelfEvolvingMetaAgent(goal=task)
    result = await agent.run()
    
    print(f"\n✅ Status: {result['status']}")
    print(f"🔧 Tools generated: {result.get('tools_generated', 0)}")
    print(f"\n📝 Analysis:\n{result.get('result', 'No result')}")


async def example_creative_task():
    """Something more creative"""
    print("\n" + "="*70)
    print("🎨 EXAMPLE 5: Creative Task")
    print("="*70)
    
    task = """
    Create a tool that generates random motivational quotes by combining:
    - A beginning phrase (like "Always remember to", "Never forget that", "Success comes from")
    - A middle action (like "believe in yourself", "work hard", "stay positive")
    - An ending (like "every single day", "no matter what", "and dreams come true")
    
    Generate 5 different motivational quotes using this pattern.
    """
    
    agent = SelfEvolvingMetaAgent(goal=task)
    result = await agent.run()
    
    print(f"\n✅ Status: {result['status']}")
    print(f"🔧 Tools generated: {result.get('tools_generated', 0)}")
    print(f"\n📝 Generated quotes:\n{result.get('result', 'No result')}")


async def example_practical_utility():
    """Practical utility tool"""
    print("\n" + "="*70)
    print("🛠️ EXAMPLE 6: Practical Utility")
    print("="*70)
    
    task = """
    Create a unit converter that can convert:
    - Miles to kilometers and vice versa
    - Pounds to kilograms and vice versa
    - Fahrenheit to Celsius and vice versa
    
    Then use it to convert:
    - 100 miles to km
    - 75 kg to pounds
    - 98.6°F to Celsius
    """
    
    agent = SelfEvolvingMetaAgent(goal=task)
    result = await agent.run()
    
    print(f"\n✅ Status: {result['status']}")
    print(f"🔧 Tools generated: {result.get('tools_generated', 0)}")
    print(f"\n📝 Conversions:\n{result.get('result', 'No result')}")


async def main():
    """Run all examples"""
    print("\n🌟 OPEN-ENDED SELF-EVOLVING AGENT DEMONSTRATIONS")
    print("="*70)
    print("Watch as the agent creates whatever tools it needs to solve each task!\n")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ No API key found! Please set GEMINI_API_KEY")
        return
    
    # Run examples
    examples = [
        ("Data Analysis", example_data_analysis),
        ("Text Processing", example_text_processing),
        ("Code Generation", example_code_generation),
        ("Math Problem", example_math_problem),
        ("Creative Task", example_creative_task),
        ("Practical Utility", example_practical_utility)
    ]
    
    print("Choose an example to run:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print(f"{len(examples) + 1}. Run all examples")
    
    try:
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == str(len(examples) + 1):
            # Run all
            for name, func in examples:
                print(f"\n🚀 Running: {name}")
                try:
                    await func()
                except Exception as e:
                    print(f"❌ Error in {name}: {e}")
                await asyncio.sleep(2)  # Brief pause between examples
        else:
            # Run selected
            idx = int(choice) - 1
            if 0 <= idx < len(examples):
                name, func = examples[idx]
                print(f"\n🚀 Running: {name}")
                await func()
            else:
                print("Invalid choice!")
                
    except (ValueError, KeyboardInterrupt):
        print("\nExiting...")
    
    print("\n\n✨ Demonstration complete!")
    print("The agent successfully handled diverse tasks by creating appropriate tools.")
    print("This is the power of self-evolution - infinite adaptability!")


if __name__ == "__main__":
    asyncio.run(main())