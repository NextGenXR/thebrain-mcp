#!/usr/bin/env python3
"""
Test script to verify hybrid search fixes.
"""

import asyncio
import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_hybrid_search():
    """Test the hybrid search functionality."""
    from api_client import TheBrainAPIClient
    from handlers.hybrid_search import search_thoughts_hybrid, get_tagged_thoughts, get_brain_statistics
    
    # Initialize API client
    api_key = os.getenv("THEBRAIN_API_KEY")
    if not api_key:
        logger.error("THEBRAIN_API_KEY environment variable not set")
        return False
    
    api = TheBrainAPIClient(api_key)
    
    # Test brain ID (use your default brain or provide as env var)
    brain_id = os.getenv("THEBRAIN_DEFAULT_BRAIN_ID", "your-brain-id-here")
    
    logger.info("=== Testing Hybrid Search Fixes ===")
    
    # Test 1: Search for "Mega" tag
    logger.info("\n1. Testing tag search for 'Mega'...")
    try:
        result = await search_thoughts_hybrid(api, {
            "brainId": brain_id,
            "queryText": "tag:Mega"
        })
        if result.get("success"):
            logger.info(f"✓ Tag search successful: Found {result.get('count', 0)} results")
            logger.info(f"  Search type: {result.get('searchType')}")
            logger.info(f"  Using local DB: {result.get('usingLocalDatabase', False)}")
        else:
            logger.warning(f"✗ Tag search failed: {result.get('error')}")
    except Exception as e:
        logger.error(f"✗ Tag search error: {e}")
    
    # Test 2: Get tagged thoughts directly
    logger.info("\n2. Testing get_tagged_thoughts for 'Mega'...")
    try:
        result = await get_tagged_thoughts(api, {
            "brainId": brain_id,
            "tagName": "Mega"
        })
        if result.get("success"):
            logger.info(f"✓ Get tagged thoughts successful: Found {result.get('count', 0)} thoughts")
            if result.get('thoughts'):
                logger.info(f"  First thought: {result['thoughts'][0].get('name', 'Unknown')}")
        else:
            logger.warning(f"✗ Get tagged thoughts failed: {result.get('error')}")
    except Exception as e:
        logger.error(f"✗ Get tagged thoughts error: {e}")
    
    # Test 3: General search (should not cause recursion)
    logger.info("\n3. Testing general search for 'Omniverse'...")
    try:
        result = await search_thoughts_hybrid(api, {
            "brainId": brain_id,
            "queryText": "Omniverse",
            "maxResults": 10
        })
        if result.get("success"):
            logger.info(f"✓ General search successful: Found {result.get('count', 0)} results")
            logger.info(f"  Using local DB: {result.get('usingLocalDatabase', False)}")
        else:
            logger.warning(f"✗ General search returned error: {result.get('error')}")
            logger.info(f"  Fallback note: {result.get('fallbackNote')}")
    except Exception as e:
        logger.error(f"✗ General search error: {e}")
    
    # Test 4: Get brain statistics (tests SQL fixes)
    logger.info("\n4. Testing brain statistics...")
    try:
        result = await get_brain_statistics(api, {
            "brainId": brain_id
        })
        if result.get("success"):
            stats = result.get("statistics", {})
            logger.info(f"✓ Brain statistics successful:")
            logger.info(f"  Total thoughts: {stats.get('totalThoughts', 0)}")
            logger.info(f"  Total tags: {stats.get('totalTags', 0)}")
            logger.info(f"  Total links: {stats.get('totalLinks', 0)}")
            logger.info(f"  Tagged thoughts: {stats.get('taggedThoughts', 0)}")
        else:
            logger.warning(f"✗ Brain statistics failed: {result.get('error')}")
    except Exception as e:
        logger.error(f"✗ Brain statistics error: {e}")
    
    # Test 5: Performance test - multiple searches
    logger.info("\n5. Testing performance with multiple searches...")
    import time
    
    search_terms = ["Digital Twins", "Isaac Sim", "Robotics", "tag:Omniverse", "recent:7"]
    start_time = time.time()
    
    for term in search_terms:
        try:
            result = await search_thoughts_hybrid(api, {
                "brainId": brain_id,
                "queryText": term,
                "maxResults": 5
            })
            if result.get("success"):
                logger.info(f"  ✓ '{term}': {result.get('count', 0)} results")
            else:
                logger.info(f"  ✗ '{term}': {result.get('error', 'Failed')}")
        except Exception as e:
            logger.info(f"  ✗ '{term}': Exception - {e}")
    
    elapsed_time = time.time() - start_time
    logger.info(f"\n✓ Completed {len(search_terms)} searches in {elapsed_time:.2f} seconds")
    logger.info(f"  Average: {elapsed_time/len(search_terms):.2f} seconds per search")
    
    logger.info("\n=== Test Complete ===")
    return True


async def main():
    """Main entry point."""
    try:
        success = await test_hybrid_search()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
