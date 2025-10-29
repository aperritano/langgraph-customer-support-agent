#!/usr/bin/env python3
"""
Graph visualization script for the Customer Support Bot.

This script generates a visual representation of the LangGraph workflow
using Mermaid diagrams. It shows the nodes, edges, and decision points
in the ReAct pattern implementation.
"""

import sys
from pathlib import Path

# Add src to path so we can import the agent
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from support_agent.agent import graph

def visualize_graph():
    """Generate and display the graph visualization."""
    print("🎨 Generating Customer Support Bot Graph Visualization...")
    print("=" * 60)
    
    try:
        # Try to display the graph using IPython
        from IPython.display import Image, display
        
        print("📊 Displaying graph with Mermaid visualization...")
        display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
        
    except ImportError:
        print("❌ IPython not available. Installing required dependencies...")
        print("Run: pip install ipython")
        
    except Exception as e:
        print(f"❌ Error generating visualization: {e}")
        print("\n🔧 This requires some extra dependencies and is optional.")
        print("To install the required dependencies:")
        print("  pip install ipython pillow")
        print("  pip install 'langgraph[visualization]'")
        
        # Fallback: Print graph structure as text
        print_graph_structure()
    
    print("\n✅ Graph visualization complete!")

def print_graph_structure():
    """Print the graph structure as text when visualization fails."""
    print("\n📋 Graph Structure (Text Representation):")
    print("-" * 40)
    print("""
    START
      ↓
   [AGENT] ← Reasoning step: decide to call tools or answer
      ↓
   {should_continue?}
     ↙        ↘
 [TOOLS]    [END]
    ↓
 [AGENT] ← Loop back with tool results
    
    ReAct Pattern Flow:
    1. Agent receives customer message
    2. Agent decides: call tools OR provide answer
    3. If tools needed → execute tools → back to agent
    4. If answer ready → end conversation turn
    5. Loop continues until final answer provided
    """)

def print_graph_info():
    """Print detailed information about the graph."""
    print("\n📊 Graph Information:")
    print("-" * 30)
    
    # Get graph structure
    graph_structure = graph.get_graph()
    
    print(f"Nodes: {list(graph_structure.nodes.keys())}")
    print(f"Edges: {len(graph_structure.edges)}")
    
    print("\n🔧 Available Tools:")
    from support_agent.tools import tools
    for tool in tools:
        print(f"  • {tool.name}: {tool.description}")

if __name__ == "__main__":
    print("🚀 Customer Support Bot - Graph Visualization")
    print("=" * 50)
    
    # Print graph information
    print_graph_info()
    
    # Try to visualize
    visualize_graph()
    
    print("\n💡 Tips:")
    print("  • The graph shows the ReAct (Reasoning + Acting) pattern")
    print("  • Agent node makes decisions about tool usage")
    print("  • Tools node executes the selected tools")
    print("  • Conditional edges control the flow")
    print("  • Loop continues until agent provides final answer")
