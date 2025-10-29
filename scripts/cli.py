#!/usr/bin/env python
"""Interactive CLI for customer support bot.

WHAT THIS FILE DOES:
Provides a command-line interface for interacting with the customer support agent.
You can chat with the agent directly from your terminal, similar to a chat application.

WHY IT'S IMPORTANT:
Allows you to test and demo the agent without needing a web interface or API.
Great for development, debugging, and demonstrating the agent's capabilities.

Run: python scripts/cli.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path so we can import from the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.messages import HumanMessage
from src.support_agent import graph


def print_banner():
    """
    Print welcome banner.
    
    WHAT IT DOES:
    Displays instructions to help users understand how to use the CLI.
    
    WHY IT'S IMPORTANT:
    Without clear instructions, users wouldn't know what commands are available
    or how to interact with the bot.
    """
    print("\n" + "=" * 70)
    print("🛍️  CUSTOMER SUPPORT BOT - Interactive CLI")
    print("=" * 70)
    print("\nCommands:")
    print("  • Type your message and press Enter")
    print("  • 'quit' or 'exit' - End conversation")
    print("  • 'new' - Start new conversation")
    print("  • 'help' - Show this help")
    print("\n" + "=" * 70 + "\n")


async def run_cli():
    """
    Run interactive CLI.
    
    WHAT IT DOES:
    Main interactive loop that:
    1. Gets customer input from terminal
    2. Sends it to the agent graph
    3. Streams the agent's response back
    4. Shows tool calls as they happen
    5. Handles special commands (quit, new session, help)
    
    WHY IT'S IMPORTANT:
    This is the user-facing interface. It orchestrates the conversation flow,
    maintains session state (using thread_id), and provides real-time feedback
    as the agent processes requests and uses tools.
    
    HOW IT WORKS:
    - Uses asyncio for async operations (required by LangGraph's streaming)
    - Maintains a session ID (thread_id) to preserve conversation context
    - Streams responses so users see updates in real-time
    - Shows tool usage so users understand what the agent is doing
    """
    print_banner()
    
    # Get session ID
    session_id = input("Enter customer ID (or press Enter for demo): ").strip()
    if not session_id:
        session_id = "demo-customer"
    
    config = {"configurable": {"thread_id": session_id}}
    
    print(f"\n✅ Session started: {session_id}")
    print("Type your message below:\n")
    
    while True:
        try:
            # Get user input
            user_input = input("💬 You: ").strip()
            
            # Handle commands
            if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
                print("\n👋 Thank you for contacting support! Have a great day!\n")
                break
            
            if user_input.lower() == "new":
                session_id = input("Enter new customer ID: ").strip() or "demo-customer"
                config = {"configurable": {"thread_id": session_id}}
                print(f"\n✅ New session started: {session_id}\n")
                continue
            
            if user_input.lower() == "help":
                print_banner()
                continue
            
            if not user_input:
                continue
            
            print()  # Blank line
            
            # Track tool calls
            tool_calls_made = []
            
            # Stream the bot's response
            async for event in graph.astream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="values",
            ):
                last_msg = event["messages"][-1]
                
                # Show tool calls
                if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                    for tc in last_msg.tool_calls:
                        tool_name = tc["name"]
                        if tool_name not in tool_calls_made:
                            print(f"🔧 Using tool: {tool_name}...")
                            tool_calls_made.append(tool_name)
                
                # Show final response (only AI messages, not tool results)
                elif (
                    hasattr(last_msg, "content")
                    and last_msg.content
                    and last_msg.type == "ai"
                ):
                    print(f"🤖 Bot: {last_msg.content}\n")
        
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted. Goodbye!\n")
            break
        
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            print("Please try again or type 'quit' to exit.\n")


def main():
    """Main entry point."""
    try:
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
