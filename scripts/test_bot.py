#!/usr/bin/env python
"""Test script for customer support bot with example conversations.

Run: python scripts/test_bot.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.messages import HumanMessage
from src.support_agent import graph


# Test conversations covering different scenarios
TEST_CONVERSATIONS = [
    {
        "name": "Policy Question",
        "messages": ["Hi, what's your return policy?"],
    },
    {
        "name": "Order Tracking",
        "messages": [
            "I need to check on my order",
            "Order number is 123456",
        ],
    },
    {
        "name": "Return Request",
        "messages": [
            "I want to return order #789012",
            "It was delivered but I changed my mind",
        ],
    },
    {
        "name": "Product Availability",
        "messages": [
            "Do you have laptops in stock?",
            "What about headphones?",
        ],
    },
    {
        "name": "Defective Item",
        "messages": [
            "My order #345678 arrived broken",
            "I want a refund immediately",
        ],
    },
    {
        "name": "Escalation (Angry Customer)",
        "messages": [
            "This is ridiculous! I've been waiting for weeks and still no order!",
            "I want to speak to a manager NOW!",
        ],
    },
    {
        "name": "Multiple Questions",
        "messages": [
            "Do you have free shipping and what's your warranty policy?",
        ],
    },
    {
        "name": "Complex Scenario",
        "messages": [
            "I ordered a laptop but received headphones instead",
            "My order number is 123456",
            "I want to return it and get the correct item",
        ],
    },
]


async def run_test_conversation(conversation: dict):
    """Run a single test conversation."""
    print("\n" + "=" * 70)
    print(f"🧪 Test: {conversation['name']}")
    print("=" * 70 + "\n")
    
    # Use conversation name as thread ID
    thread_id = conversation["name"].lower().replace(" ", "-")
    config = {"configurable": {"thread_id": thread_id}}
    
    for i, message in enumerate(conversation["messages"], 1):
        print(f"💬 Message {i}: {message}")
        print("-" * 70)
        
        # Track what happens
        tool_calls_made = []
        
        # Run the conversation turn
        async for event in graph.astream(
            {"messages": [HumanMessage(content=message)]},
            config=config,
            stream_mode="values",
        ):
            last_msg = event["messages"][-1]
            
            # Track tool calls
            if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                for tc in last_msg.tool_calls:
                    tool_name = tc["name"]
                    if tool_name not in tool_calls_made:
                        print(f"   🔧 Tool: {tool_name}")
                        tool_calls_made.append(tool_name)
            
            # Show final response
            elif hasattr(last_msg, "content") and last_msg.content and last_msg.type == "ai":
                print(f"\n🤖 Bot Response:")
                print(f"   {last_msg.content}\n")
        
        # Show summary of what happened
        if tool_calls_made:
            print(f"📊 Tools used: {', '.join(tool_calls_made)}")
        print()


async def run_all_tests():
    """Run all test conversations."""
    print("\n" + "=" * 70)
    print("🚀 CUSTOMER SUPPORT BOT - TEST SUITE")
    print("=" * 70)
    print(f"\nRunning {len(TEST_CONVERSATIONS)} test conversations...\n")
    
    for i, conversation in enumerate(TEST_CONVERSATIONS, 1):
        await run_test_conversation(conversation)
        
        # Add a pause between tests for readability
        if i < len(TEST_CONVERSATIONS):
            await asyncio.sleep(0.5)
    
    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70 + "\n")


async def run_single_test():
    """Run a single interactive test."""
    print("\n" + "=" * 70)
    print("🧪 SINGLE TEST MODE")
    print("=" * 70 + "\n")
    
    # Show available tests
    print("Available test scenarios:")
    for i, conv in enumerate(TEST_CONVERSATIONS, 1):
        print(f"  {i}. {conv['name']}")
    print()
    
    # Get user choice
    try:
        choice = int(input("Select test number (or 0 for all): ").strip())
        
        if choice == 0:
            await run_all_tests()
        elif 1 <= choice <= len(TEST_CONVERSATIONS):
            await run_test_conversation(TEST_CONVERSATIONS[choice - 1])
        else:
            print("Invalid choice. Running all tests...")
            await run_all_tests()
    
    except ValueError:
        print("Invalid input. Running all tests...")
        await run_all_tests()


async def run_custom_test():
    """Run a custom test conversation."""
    print("\n" + "=" * 70)
    print("🎯 CUSTOM TEST MODE")
    print("=" * 70 + "\n")
    
    messages = []
    
    print("Enter messages (empty line to finish):")
    while True:
        msg = input(f"  Message {len(messages) + 1}: ").strip()
        if not msg:
            break
        messages.append(msg)
    
    if not messages:
        print("No messages entered. Exiting.")
        return
    
    # Run custom conversation
    custom_conv = {"name": "Custom Test", "messages": messages}
    await run_test_conversation(custom_conv)


def main():
    """Main entry point."""
    print("\n🤖 Customer Support Bot - Test Runner\n")
    print("Modes:")
    print("  1. Run all tests")
    print("  2. Run single test")
    print("  3. Custom test")
    print()
    
    mode = input("Select mode (1/2/3): ").strip()
    
    try:
        if mode == "1":
            asyncio.run(run_all_tests())
        elif mode == "2":
            asyncio.run(run_single_test())
        elif mode == "3":
            asyncio.run(run_custom_test())
        else:
            print("Invalid mode. Running all tests...")
            asyncio.run(run_all_tests())
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user.\n")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ Error running tests: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
