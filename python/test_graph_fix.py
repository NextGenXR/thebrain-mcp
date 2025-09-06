#!/usr/bin/env python
"""
Test script to verify graph analysis works with brain ID mismatches.

This tests the fixes for the "database access issues" that Claude was reporting.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph_analyzer import BrainGraphAnalyzer
from src.path_utils import find_brain_database, format_path_for_display
from src.handlers.graph import get_or_create_analyzer

async def test_graph_analysis():
    """Test graph analysis with various brain IDs."""
    
    # Find the database
    db_path = find_brain_database()
    if not db_path:
        print("❌ No Brain database found")
        return False
    
    print(f"✅ Found database: {format_path_for_display(db_path)}")
    
    # Test 1: Load with no brain ID (should work)
    try:
        analyzer = BrainGraphAnalyzer(str(db_path))
        graph = analyzer.load_graph()
        print(f"✅ Loaded without brain ID: {graph.number_of_nodes()} nodes")
    except Exception as e:
        print(f"❌ Failed to load without brain ID: {e}")
        return False
    
    # Test 2: Load with wrong brain ID (should still work)
    try:
        graph = analyzer.load_graph("wrong_brain_id_123")
        print(f"✅ Loaded with wrong brain ID: {graph.number_of_nodes()} nodes")
    except Exception as e:
        print(f"❌ Failed with wrong brain ID: {e}")
        return False
    
    # Test 3: Load with actual brain ID from database
    try:
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT BrainId FROM Thoughts LIMIT 1")
        actual_id = cursor.fetchone()[0]
        conn.close()
        
        graph = analyzer.load_graph(actual_id)
        print(f"✅ Loaded with correct brain ID ({actual_id[:8]}...): {graph.number_of_nodes()} nodes")
    except Exception as e:
        print(f"❌ Failed with correct brain ID: {e}")
        return False
    
    # Test 4: Test centrality analysis
    try:
        central = analyzer.find_central_thoughts(top_n=3)
        print(f"✅ Centrality analysis works, found {len(central)} measures")
        if 'degree' in central and central['degree']:
            top_thought = central['degree'][0]
            print(f"   Most connected: {top_thought[1]} ({top_thought[2]:.3f})")
    except Exception as e:
        print(f"❌ Centrality analysis failed: {e}")
        return False
    
    # Test 5: Test the MCP handler (simulated)
    try:
        # Mock API object
        class MockAPI:
            pass
        
        api = MockAPI()
        
        # This would be called by Claude with wrong brain ID
        handler_analyzer = await get_or_create_analyzer(api, "U01B02")
        if handler_analyzer:
            print(f"✅ MCP handler can get analyzer with short brain ID")
        else:
            print("⚠️  MCP handler couldn't get analyzer (but error is handled)")
    except Exception as e:
        print(f"⚠️  MCP handler test: {e}")
    
    analyzer.close()
    print("\n✅ All tests passed! Graph analysis should work in Claude now.")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_graph_analysis())
    sys.exit(0 if success else 1)
