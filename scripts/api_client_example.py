#!/usr/bin/env python
"""Example API client for customer support bot.

This demonstrates how to interact with the LangGraph Dev API programmatically.

Prerequisites:
- Bot running: langgraph dev
- requests library: pip install requests

Run: python scripts/api_client_example.py
"""

import requests
import json
import time
from typing import Optional


class SupportBotClient:
    """Client for interacting with the customer support bot API."""
    
    def __init__(self, base_url: str = "http://localhost:8123"):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the LangGraph Dev server
        """
        self.base_url = base_url
    
    def create_thread(self) -> str:
        """
        Create a new conversation thread.
        
        Returns:
            Thread ID for the conversation
        """
        response = requests.post(f"{self.base_url}/threads")
        response.raise_for_status()
        return response.json()["thread_id"]
    
    def send_message(
        self,
        message: str,
        thread_id: str,
        stream: bool = False
    ) -> dict:
        """
        Send a message to the bot.
        
        Args:
            message: User's message
            thread_id: Conversation thread ID
            stream: Whether to stream the response
        
        Returns:
            Bot's response and metadata
        """
        payload = {
            "input": {
                "messages": [{"role": "user", "content": message}]
            },
            "config": {
                "configurable": {
                    "thread_id": thread_id
                }
            },
            "stream_mode": "values" if stream else None
        }
        
        response = requests.post(
            f"{self.base_url}/threads/{thread_id}/runs",
            json=payload,
            stream=stream
        )
        response.raise_for_status()
        
        if stream:
            return self._handle_streaming_response(response)
        else:
            return response.json()
    
    def _handle_streaming_response(self, response):
        """Handle streaming response from the API."""
        results = []
        
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                    results.append(data)
                    
                    # Print streaming updates
                    if "messages" in data:
                        last_msg = data["messages"][-1]
                        if last_msg.get("type") == "ai":
                            print(f"🤖 {last_msg['content']}")
                        elif last_msg.get("tool_calls"):
                            for tc in last_msg["tool_calls"]:
                                print(f"🔧 Using tool: {tc['name']}")
                
                except json.JSONDecodeError:
                    continue
        
        return results[-1] if results else {}
    
    def get_thread_history(self, thread_id: str) -> list:
        """
        Get conversation history for a thread.
        
        Args:
            thread_id: Thread ID
        
        Returns:
            List of messages in the conversation
        """
        response = requests.get(f"{self.base_url}/threads/{thread_id}/history")
        response.raise_for_status()
        return response.json()
    
    def get_thread_state(self, thread_id: str) -> dict:
        """
        Get current state of a thread.
        
        Args:
            thread_id: Thread ID
        
        Returns:
            Current state of the conversation
        """
        response = requests.get(f"{self.base_url}/threads/{thread_id}/state")
        response.raise_for_status()
        return response.json()


def example_single_message():
    """Example: Send a single message."""
    print("\n" + "=" * 70)
    print("Example 1: Single Message")
    print("=" * 70 + "\n")
    
    client = SupportBotClient()
    
    # Create conversation
    thread_id = client.create_thread()
    print(f"Created thread: {thread_id}\n")
    
    # Send message
    print("💬 User: What's your return policy?")
    result = client.send_message("What's your return policy?", thread_id)
    
    # Get bot response
    messages = result.get("messages", [])
    if messages:
        bot_response = messages[-1].get("content", "")
        print(f"🤖 Bot: {bot_response}\n")


def example_multi_turn_conversation():
    """Example: Multi-turn conversation."""
    print("\n" + "=" * 70)
    print("Example 2: Multi-turn Conversation")
    print("=" * 70 + "\n")
    
    client = SupportBotClient()
    thread_id = client.create_thread()
    print(f"Thread: {thread_id}\n")
    
    # Conversation flow
    messages = [
        "Hi, I need help with my order",
        "Order number is 123456",
        "When will it arrive?",
    ]
    
    for msg in messages:
        print(f"💬 User: {msg}")
        result = client.send_message(msg, thread_id)
        
        if "messages" in result:
            bot_msg = result["messages"][-1].get("content", "")
            print(f"🤖 Bot: {bot_msg}\n")
        
        time.sleep(0.5)  # Small delay for readability


def example_streaming():
    """Example: Streaming responses."""
    print("\n" + "=" * 70)
    print("Example 3: Streaming Response")
    print("=" * 70 + "\n")
    
    client = SupportBotClient()
    thread_id = client.create_thread()
    
    print("💬 User: Can you check order #123456 and tell me about your warranty?\n")
    
    # Send with streaming enabled
    client.send_message(
        "Can you check order #123456 and tell me about your warranty?",
        thread_id,
        stream=True
    )
    print()


def example_conversation_history():
    """Example: Retrieve conversation history."""
    print("\n" + "=" * 70)
    print("Example 4: Conversation History")
    print("=" * 70 + "\n")
    
    client = SupportBotClient()
    thread_id = client.create_thread()
    
    # Have a conversation
    client.send_message("What's your return policy?", thread_id)
    client.send_message("How long does shipping take?", thread_id)
    
    # Get history
    history = client.get_thread_history(thread_id)
    
    print("Conversation History:")
    for i, msg in enumerate(history.get("values", []), 1):
        messages = msg.get("messages", [])
        if messages:
            last = messages[-1]
            role = "User" if last.get("type") == "human" else "Bot"
            content = last.get("content", "")[:100]  # Truncate for display
            print(f"{i}. {role}: {content}...\n")


def example_error_handling():
    """Example: Handle errors gracefully."""
    print("\n" + "=" * 70)
    print("Example 5: Error Handling")
    print("=" * 70 + "\n")
    
    client = SupportBotClient()
    
    try:
        # Try to send message without creating thread
        client.send_message("Hello", "invalid-thread-id")
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error: {e}")
        print("Handling error: Creating new thread...\n")
        
        # Recover by creating valid thread
        thread_id = client.create_thread()
        result = client.send_message("Hello", thread_id)
        print("✅ Successfully sent message after error recovery\n")


def main():
    """Run all examples."""
    print("\n🤖 Customer Support Bot - API Client Examples")
    print("\nMake sure the bot is running: langgraph dev\n")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8123/health", timeout=2)
        response.raise_for_status()
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("❌ Error: Bot is not running!")
        print("\nStart the bot first:")
        print("  langgraph dev\n")
        return
    
    print("✅ Bot is running. Starting examples...\n")
    
    # Run examples
    try:
        example_single_message()
        input("Press Enter to continue...")
        
        example_multi_turn_conversation()
        input("Press Enter to continue...")
        
        example_streaming()
        input("Press Enter to continue...")
        
        example_conversation_history()
        input("Press Enter to continue...")
        
        example_error_handling()
        
        print("\n" + "=" * 70)
        print("✅ All examples completed!")
        print("=" * 70 + "\n")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user.\n")
    
    except Exception as e:
        print(f"\n❌ Error: {e}\n")


if __name__ == "__main__":
    main()
