#!/usr/bin/env python3
"""
Simple test script to verify TheBrain MCP server installation.
"""

import sys
import asyncio
from pathlib import Path

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from src.api_client import TheBrainAPI
        print("✓ API client imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import API client: {e}")
        return False
    
    try:
        from src.tool_schemas import get_tool_schemas
        schemas = get_tool_schemas()
        print(f"✓ Tool schemas imported successfully ({len(schemas)} tools found)")
    except ImportError as e:
        print(f"✗ Failed to import tool schemas: {e}")
        return False
    
    try:
        from src import handlers
        print("✓ Handlers imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import handlers: {e}")
        return False
    
    try:
        import mcp
        print("✓ MCP SDK imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import MCP SDK: {e}")
        print("  Please install requirements: pip install -r requirements.txt")
        return False
    
    return True


def test_environment():
    """Test environment configuration."""
    print("\nTesting environment configuration...")
    
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    env_file = Path(".env")
    if env_file.exists():
        load_dotenv()
        print("✓ .env file found")
    else:
        print("⚠ .env file not found (will use system environment variables)")
    
    # Check for API key
    api_key = os.getenv("THEBRAIN_API_KEY")
    if api_key:
        masked_key = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
        print(f"✓ THEBRAIN_API_KEY found: {masked_key}")
    else:
        print("✗ THEBRAIN_API_KEY not found")
        print("  Please set THEBRAIN_API_KEY in .env file or environment variables")
        return False
    
    # Check for optional default brain ID
    default_brain = os.getenv("THEBRAIN_DEFAULT_BRAIN_ID")
    if default_brain:
        print(f"✓ THEBRAIN_DEFAULT_BRAIN_ID found: {default_brain}")
    else:
        print("ℹ THEBRAIN_DEFAULT_BRAIN_ID not set (optional)")
    
    return True


async def test_api_client():
    """Test basic API client functionality."""
    print("\nTesting API client...")
    
    import os
    from dotenv import load_dotenv
    from src.api_client import TheBrainAPI
    
    load_dotenv()
    api_key = os.getenv("THEBRAIN_API_KEY")
    
    if not api_key:
        print("⚠ Skipping API test (no API key)")
        return True
    
    try:
        api = TheBrainAPI(api_key)
        print("✓ API client created successfully")
        
        # Test a simple API call
        print("  Testing API connection...")
        try:
            brains = await api.list_brains()
            print(f"✓ API connection successful ({len(brains)} brains found)")
        except Exception as e:
            print(f"✗ API connection failed: {e}")
            print("  Please verify your API key is correct")
            return False
        finally:
            await api.close()
            
    except Exception as e:
        print(f"✗ Failed to create API client: {e}")
        return False
    
    return True


def test_tool_schemas():
    """Test tool schema definitions."""
    print("\nTesting tool schemas...")
    
    from src.tool_schemas import get_tool_schemas
    
    schemas = get_tool_schemas()
    
    # Check for expected tools
    expected_tools = [
        "list_brains", "create_thought", "search_thoughts",
        "create_link", "add_file_attachment", "get_note"
    ]
    
    for tool in expected_tools:
        if tool in schemas:
            print(f"✓ Tool '{tool}' found")
        else:
            print(f"✗ Tool '{tool}' missing")
            return False
    
    print(f"✓ All {len(schemas)} tools validated")
    return True


async def main():
    """Run all tests."""
    print("=" * 50)
    print("TheBrain MCP Server - Installation Test")
    print("=" * 50)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test environment
    if not test_environment():
        all_passed = False
    
    # Test tool schemas
    if not test_tool_schemas():
        all_passed = False
    
    # Test API client (if configured)
    if not await test_api_client():
        all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✓ All tests passed! The server is ready to use.")
        print("\nTo run the server:")
        print("  python main.py")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
