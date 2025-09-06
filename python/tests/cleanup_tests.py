#!/usr/bin/env python3
"""
Script to organize and clean up test files.
Run this to consolidate test files as recommended.
"""

import os
import shutil
from pathlib import Path

def main():
    """Organize test files."""
    
    print("=" * 60)
    print("TheBrain MCP Test Files Organization")
    print("=" * 60)
    print()
    
    # Define test categories
    essential_tests = [
        "test_installation.py",
        "test_api.py", 
        "test_graph_analysis.py",
        "test_hybrid_fix.py"
    ]
    
    redundant_tests = [
        "test_search_simple.py",
        "test_server.py"
    ]
    
    # Show current status
    print("Current test files:")
    test_files = list(Path(".").glob("test*.py"))
    for tf in test_files:
        if tf.name in essential_tests:
            print(f"  ✅ {tf.name} [KEEP]")
        elif tf.name in redundant_tests:
            print(f"  ❌ {tf.name} [REDUNDANT]")
        else:
            print(f"  ❓ {tf.name} [UNKNOWN]")
    
    print()
    print("Recommendation:")
    print(f"  - Keep {len(essential_tests)} essential test files")
    print(f"  - Remove {len(redundant_tests)} redundant test files")
    print()
    
    # Ask user what to do
    print("Options:")
    print("  1. Create 'tests/' directory and organize files")
    print("  2. Remove redundant test files")
    print("  3. Both (recommended)")
    print("  4. Do nothing (just show info)")
    print()
    
    choice = input("Choose option (1-4): ").strip()
    
    if choice in ["1", "3"]:
        # Create tests directory
        tests_dir = Path("tests")
        tests_dir.mkdir(exist_ok=True)
        
        # Create __init__.py
        (tests_dir / "__init__.py").write_text('"""Test suite for TheBrain MCP."""\n')
        
        # Copy essential tests
        print("\nOrganizing tests...")
        for test_file in essential_tests:
            if Path(test_file).exists():
                shutil.copy2(test_file, tests_dir / test_file)
                print(f"  ✓ Copied {test_file} to tests/")
        
        # Move the README
        if Path("tests/README_TEST_FILES.md").exists():
            shutil.move("tests/README_TEST_FILES.md", tests_dir / "README.md")
            print(f"  ✓ Moved test documentation to tests/")
    
    if choice in ["2", "3"]:
        # Remove redundant files
        print("\nRemoving redundant test files...")
        for test_file in redundant_tests:
            if Path(test_file).exists():
                # Create backup first
                backup_name = f"_backup_{test_file}"
                shutil.copy2(test_file, backup_name)
                os.remove(test_file)
                print(f"  ✓ Removed {test_file} (backup: {backup_name})")
    
    if choice == "4":
        print("\nNo changes made.")
    
    if choice in ["1", "2", "3"]:
        print("\n" + "=" * 60)
        print("✅ Test organization complete!")
        print("=" * 60)
        print()
        print("To run tests:")
        print("  uv run python test_installation.py    # Verify setup")
        print("  uv run python test_api.py            # Check API")
        print("  uv run python test_graph_analysis.py  # Test graphs")
        print("  uv run python test_hybrid_fix.py     # Test hybrid")

if __name__ == "__main__":
    main()
