#!/usr/bin/env python3
"""
Graph visualization script for the Customer Support Bot.

This script generates a visual representation of the LangGraph workflow
using Mermaid diagrams. It shows the nodes, edges, and decision points
in the ReAct pattern implementation.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path so `src.*` imports work when running directly
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.support_agent.agent import graph

def visualize_graph():
    """Generate and save the graph visualization to images directory."""
    print("🎨 Generating Customer Support Bot Graph Visualization...")
    print("=" * 60)
    
    # Determine output path
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    images_dir = project_root / "images"
    images_dir.mkdir(exist_ok=True)  # Create images directory if it doesn't exist
    
    output_path = images_dir / "langgraph-graph-mermaid.png"
    
    try:
        print("📊 Generating graph visualization...")
        # Generate the PNG image
        png_bytes = graph.get_graph(xray=True).draw_mermaid_png()
        
        # Save to file
        with open(output_path, "wb") as f:
            f.write(png_bytes)
        
        print(f"✅ Graph visualization saved to: {output_path}")
        
        # Try to display in IPython if available
        try:
            from IPython.display import Image, display
            print("📺 Displaying in IPython...")
            display(Image(output_path))
        except ImportError:
            print("💡 (IPython not available - image saved but not displayed)")
        except Exception:
            pass  # Silently ignore if not in IPython environment
        
    except ImportError:
        print("❌ Missing dependencies. Install with:")
        print("  pip install ipython pillow")
        print("  pip install 'langgraph[visualization]'")
        
        # Fallback: Print graph structure as text
        print_graph_structure()
        
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
   {should_send_greeting?} ← Check if greeting needed
      ↙              ↘
 [GREETING]        [AGENT] ← Existing conversation
      ↓
   {should_continue_after_greeting?} ← User message waiting?
      ↙              ↘
   [AGENT]         [END] ← Greeting complete, wait for user
      ↓
   {should_continue?} ← Agent decides: call tools OR answer?
      ↙        ↘
   [TOOLS]    [END]
      ↓
   [AGENT] ← Loop back with tool results
    
    Flow Description:
    1. Agent receives customer message
    2. Agent decides: call tools OR provide answer
    3. On first interaction, agent uses send_greeting tool automatically
    4. If tools needed → execute tools → back to agent
    5. If answer ready → end conversation turn
    6. Loop continues until final answer provided
    
    Note: Greeting is handled via the send_greeting tool, which the agent
    automatically calls on the first interaction.
    """)

def print_graph_info():
    """Print detailed information about the graph."""
    print("\n📊 Graph Information:")
    print("-" * 30)
    
    # Get graph structure
    graph_structure = graph.get_graph()
    
    nodes = list(graph_structure.nodes.keys())
    print(f"Nodes ({len(nodes)}):")
    for node in nodes:
        print(f"  • {node}")
    
    # Get edges safely
    edges = getattr(graph_structure, 'edges', {})
    edges_count = len(edges) if edges else 0
    print(f"\nEdges: {edges_count} direct edges")
    
    # Try to access conditional edges if available
    conditional_edges_count = 0
    try:
        # Different LangGraph versions may have different attributes
        if hasattr(graph_structure, 'conditional_edges'):
            conditional_edges = graph_structure.conditional_edges
            conditional_edges_count = len(conditional_edges) if conditional_edges else 0
        elif hasattr(graph_structure, 'branches'):
            conditional_edges_count = len(graph_structure.branches)
    except (AttributeError, TypeError, KeyError):
        pass
    
    if conditional_edges_count > 0:
        print(f"Conditional Edges: {conditional_edges_count} decision points")
    else:
        # We know we have conditional edges (should_send_greeting, should_continue, etc.)
        print("Conditional Edges: 3 decision points (should_send_greeting, should_continue_after_greeting, should_continue)")
    
    # Print edge details if possible
    if edges and isinstance(edges, dict):
        print("\n📎 Edge Details:")
        try:
            for source, targets in edges.items():
                if isinstance(targets, (list, tuple)):
                    for target in targets:
                        print(f"  • {source} → {target}")
                else:
                    print(f"  • {source} → {targets}")
        except (AttributeError, TypeError):
            print("  (Edge structure not directly accessible)")
    elif edges:
        # If edges is not a dict, try to represent it
        print("\n📎 Edge Details:")
        print(f"  (Edges structure: {type(edges).__name__})")
    
    print("\n🔧 Available Tools:")
    from src.support_agent.tools import tools
    for tool in tools:
        print(f"  • {tool.name}")
        # Truncate description if too long
        desc = tool.description[:60] + "..." if len(tool.description) > 60 else tool.description
        print(f"    {desc}")

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
    print("  • Agent automatically uses send_greeting tool on first interaction")
    print("  • Tools node executes the selected tools")
    print("  • Conditional edges control the flow")
    print("  • Loop continues until agent provides final answer")
