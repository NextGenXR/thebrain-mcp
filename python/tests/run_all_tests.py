#!/usr/bin/env python3
"""
Master test runner for TheBrain MCP.
Runs all essential tests in sequence and provides a summary.
"""

import asyncio
import sys
import os
from pathlib import Path
import time
from typing import Dict, Tuple

# Add parent directory to path for src imports
sys.path.insert(0, str(Path(__file__).parent.parent))


async def run_test(test_name: str, test_func) -> Tuple[bool, float, str]:
    """
    Run a single test and return results.
    
    Returns:
        Tuple of (success, duration, message)
    """
    print(f"\n{'='*60}")
    print(f"Running: {test_name}")
    print('='*60)
    
    start_time = time.time()
    try:
        result = await test_func() if asyncio.iscoroutinefunction(test_func) else test_func()
        duration = time.time() - start_time
        
        if result is False:
            return (False, duration, "Test failed")
        return (True, duration, "Test passed")
    except Exception as e:
        duration = time.time() - start_time
        return (False, duration, f"Exception: {str(e)}")


async def main():
    """Run all tests and provide summary."""
    print("="*70)
    print(" TheBrain MCP - Comprehensive Test Suite")
    print("="*70)
    
    # Check for API key first
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("THEBRAIN_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: THEBRAIN_API_KEY not found in environment")
        print("Some tests will fail without a valid API key.")
        print("Create a .env file with: THEBRAIN_API_KEY=your-key-here")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    results: Dict[str, Tuple[bool, float, str]] = {}
    
    # Test 1: Installation
    print("\n" + "="*70)
    print("TEST 1/4: Installation Verification")
    print("-"*70)
    try:
        # Import test modules
        sys.path.insert(0, str(Path(__file__).parent))
        from test_installation import test_imports, test_environment
        success = test_imports() and test_environment()
        results["Installation"] = (success, 0, "All components installed" if success else "Missing components")
    except Exception as e:
        results["Installation"] = (False, 0, str(e))
    
    # Test 2: API Connection (if key available)
    if api_key:
        print("\n" + "="*70)
        print("TEST 2/4: API Connection")
        print("-"*70)
        try:
            from test_api import test_api
            result = await run_test("API Connection", test_api)
            results["API Connection"] = result
        except Exception as e:
            results["API Connection"] = (False, 0, str(e))
    else:
        results["API Connection"] = (False, 0, "Skipped - No API key")
    
    # Test 3: Graph Analysis
    print("\n" + "="*70)
    print("TEST 3/4: Graph Analysis Features")
    print("-"*70)
    try:
        # Check if NetworkX is installed
        import networkx as nx
        print(f"✓ NetworkX {nx.__version__} available")
        
        # Check if a Brain.db exists
        brain_db = Path.home() / "Brains" / "U01" / "B02" / "Brain.db"
        if brain_db.exists():
            print(f"✓ Local Brain database found")
            results["Graph Analysis"] = (True, 0, "Graph features available")
        else:
            print("ℹ Local Brain database not found at expected location")
            results["Graph Analysis"] = (True, 0, "Graph features available (no local DB)")
    except ImportError:
        results["Graph Analysis"] = (False, 0, "NetworkX not installed")
    
    # Test 4: Hybrid Mode (if API key and local DB available)
    print("\n" + "="*70)
    print("TEST 4/4: Hybrid Mode")
    print("-"*70)
    
    if api_key:
        try:
            # Quick test of hybrid mode
            from src.handlers.hybrid_search import get_or_create_manager
            print("✓ Hybrid mode modules available")
            results["Hybrid Mode"] = (True, 0, "Hybrid modules loaded")
        except Exception as e:
            results["Hybrid Mode"] = (False, 0, f"Hybrid mode error: {e}")
    else:
        results["Hybrid Mode"] = (False, 0, "Skipped - No API key")
    
    # Print summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r[0])
    
    for test_name, (success, duration, message) in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name:20} | {message}")
    
    print("-"*70)
    print(f"Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! TheBrain MCP is ready to use.")
    elif passed_tests >= total_tests - 1:
        print("\n✅ Core functionality working. Some optional features may be limited.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
    
    print("\n" + "="*70)
    print("Quick Start Commands:")
    print("-"*70)
    print("  uv run python main.py           # Start the MCP server")
    print("  uv run python test_api.py       # Test API connection")
    print("  uv run python test_installation.py  # Verify installation")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
