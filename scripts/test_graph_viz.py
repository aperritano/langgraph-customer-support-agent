#!/usr/bin/env python3
"""
Simple graph visualization test script.

Run this to test the graph visualization functionality.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_graph_visualization():
    """Test the graph visualization with the exact code provided."""
    try:
        from support_agent.agent import graph
        from IPython.display import Image, display
        
        print("🎨 Testing graph visualization...")
        print("=" * 40)
        
        # This is the exact code you requested
        try:
            display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
            print("✅ Graph visualization successful!")
            
        except Exception as e:
            print(f"❌ Visualization error: {e}")
            print("\n🔧 This requires some extra dependencies and is optional")
            print("To install required dependencies:")
            print("  pip install ipython pillow")
            print("  pip install 'langgraph[visualization]'")
            
            # Show text representation as fallback
            print("\n📋 Graph Structure:")
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
            """)
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
        print("and all dependencies are installed.")

if __name__ == "__main__":
    test_graph_visualization()
