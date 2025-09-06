#!/usr/bin/env python3
"""
Test TheBrain API connection and key validity.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.api_client import TheBrainAPI

async def test_api():
    """Test the API connection."""
    load_dotenv()
    
    api_key = os.getenv("THEBRAIN_API_KEY")
    if not api_key:
        print("ERROR: No API key found in .env file")
        return False
    
    print(f"Testing API with key: {api_key[:8]}...{api_key[-4:]}")
    print("=" * 50)
    
    api = TheBrainAPI(api_key)
    
    try:
        print("Testing API connection...")
        brains = await api.list_brains()
        print(f"✓ API connection successful!")
        print(f"✓ Found {len(brains)} brain(s):")
        for brain in brains:
            print(f"  - {brain.get('name', 'Unknown')} (ID: {brain.get('id', 'Unknown')})")
        return True
    except Exception as e:
        print(f"✗ API connection failed: {e}")
        print("\nPossible issues:")
        print("1. API key might be invalid or expired")
        print("2. Network connection issues")
        print("3. TheBrain API service might be down")
        print("\nPlease verify your API key at: https://www.thebrain.com/")
        return False
    finally:
        await api.close()

if __name__ == "__main__":
    success = asyncio.run(test_api())
    sys.exit(0 if success else 1)
