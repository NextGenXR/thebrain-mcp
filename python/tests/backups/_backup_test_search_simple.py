#!/usr/bin/env python3
"""
Simple test to check if search is working.
This bypasses the hybrid system and uses API directly.
"""

import asyncio
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from api_client import TheBrainAPI


async def test_search():
    """Test basic search functionality."""
    
    # Disable hybrid mode for this test
    os.environ["THEBRAIN_DISABLE_HYBRID"] = "true"
    
    # Get API key
    api_key = os.getenv("THEBRAIN_API_KEY")
    if not api_key:
        print("Error: THEBRAIN_API_KEY not found in environment")
        return
    
    print(f"Using API key: {api_key[:8]}...{api_key[-4:]}")
    
    # Create client
    client = TheBrainAPI(api_key)
    
    try:
        # List brains
        print("\n1. Getting brains...")
        brains = await client.list_brains()
        print(f"Found {len(brains)} brains")
        
        if not brains:
            print("No brains found!")
            return
        
        # Use first brain or main brain
        brain = brains[0]
        for b in brains:
            if "Main" in b.get("name", ""):
                brain = b
                break
        
        brain_id = brain.get("id")
        print(f"Using brain: {brain.get('name')} (ID: {brain_id})")
        
        # Test simple search
        print("\n2. Testing search for 'Mega'...")
        results = await client.search_thoughts(
            brain_id, 
            "Mega",
            max_results=5
        )
        
        print(f"Found {len(results)} results:")
        for i, result in enumerate(results[:5], 1):
            print(f"  {i}. {result.get('name', 'Unknown')}")
            print(f"     ID: {result.get('id', 'No ID')}")
            print(f"     Type: {result.get('entityType', 'Unknown')}")
        
        # Test tag search (though it probably won't work via API)
        print("\n3. Testing tag search for 'tag:Mega'...")
        results = await client.search_thoughts(
            brain_id,
            "tag:Mega",
            max_results=5
        )
        print(f"Found {len(results)} results for tag search")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()
        print("\nTest complete!")


if __name__ == "__main__":
    asyncio.run(test_search())
