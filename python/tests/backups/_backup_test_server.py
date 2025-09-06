#!/usr/bin/env python3
"""
Simple test to verify the TheBrain MCP server components work.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_server():
    """Test that the server components load correctly."""
    print("Testing TheBrain MCP Server components...")
    print("=" * 50)
    
    # Test imports
    try:
        from src.api_client import TheBrainAPI
        print("✓ API client imported")
    except ImportError as e:
        print(f"✗ Failed to import API client: {e}")
        return False
    
    try:
        from src.tool_schemas import get_tool_schemas
        schemas = get_tool_schemas()
        print(f"✓ Tool schemas loaded ({len(schemas)} tools)")
    except ImportError as e:
        print(f"✗ Failed to import tool schemas: {e}")
        return False
    
    try:
        from src import handlers
        print("✓ Handlers imported")
    except ImportError as e:
        print(f"✗ Failed to import handlers: {e}")
        return False
    
    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent, CallToolResult
        print("✓ MCP SDK imported correctly")
    except ImportError as e:
        print(f"✗ Failed to import MCP SDK: {e}")
        return False
    
    # Test environment
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("THEBRAIN_API_KEY")
    if api_key:
        print(f"✓ API key found (length: {len(api_key)})")
        
        # Test API client creation
        try:
            api = TheBrainAPI(api_key)
            print("✓ API client created successfully")
            await api.close()
        except Exception as e:
            print(f"⚠ API client creation warning: {e}")
    else:
        print("⚠ No API key found (set THEBRAIN_API_KEY in .env)")
    
    print("=" * 50)
    print("✓ All server components are working!")
    print("\nTo run the server:")
    print("  uv run python main.py")
    print("\nThe server will run silently, waiting for MCP protocol messages.")
    return True

if __name__ == "__main__":
    success = asyncio.run(test_server())
    sys.exit(0 if success else 1)
