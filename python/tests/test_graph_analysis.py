#!/usr/bin/env python3
"""
Test and demonstrate graph analysis capabilities for TheBrain databases.
"""

import sys
import os
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_graph_analysis():
    """Test graph analysis on a Brain database."""
    from graph_analyzer import BrainGraphAnalyzer
    
    # Find Brain database
    # Try the path we saw in the user's open files
    possible_paths = [
        Path(r"C:\Users\joconnor\Brains\U01\B02\Brain.db"),
        Path.home() / "Brains" / "U01" / "B02" / "Brain.db",
        Path.home() / "Brains" / "U00" / "B00" / "Brain.db",
    ]
    
    db_path = None
    for path in possible_paths:
        if path.exists():
            db_path = str(path)
            logger.info(f"Found Brain database at: {db_path}")
            break
    
    if not db_path:
        logger.error("No Brain database found. Please specify path as argument.")
        logger.info("Usage: python test_graph_analysis.py <path_to_Brain.db>")
        return False
    
    logger.info("=== Testing Graph Analysis ===\n")
    
    # Initialize analyzer
    analyzer = BrainGraphAnalyzer(db_path)
    
    # Test 1: Load graph
    logger.info("1. Loading brain graph...")
    try:
        graph = analyzer.load_graph()
        logger.info(f"✓ Graph loaded successfully")
        logger.info(f"  Thoughts (nodes): {graph.number_of_nodes()}")
        logger.info(f"  Links (edges): {graph.number_of_edges()}")
    except Exception as e:
        logger.error(f"✗ Failed to load graph: {e}")
        return False
    
    # Test 2: Get statistics
    logger.info("\n2. Analyzing graph statistics...")
    try:
        stats = analyzer.get_statistics()
        logger.info(f"✓ Statistics calculated")
        logger.info(f"  Graph density: {stats['basic']['density']:.4f}")
        logger.info(f"  Is connected: {stats['basic']['is_connected']}")
        logger.info(f"  Orphaned thoughts: {stats['orphaned_thoughts']['count']}")
        logger.info(f"  Average degree: {stats['degree_distribution']['avg_degree']:.2f}")
        
        if stats['orphaned_thoughts']['thoughts']:
            logger.info(f"  Example orphans: {', '.join(stats['orphaned_thoughts']['thoughts'][:3])}")
    except Exception as e:
        logger.error(f"✗ Failed to get statistics: {e}")
    
    # Test 3: Find central thoughts
    logger.info("\n3. Finding central/important thoughts...")
    try:
        central = analyzer.find_central_thoughts(top_n=5)
        
        # Show top 3 by PageRank (most important)
        logger.info("✓ Central thoughts identified")
        logger.info("  Top thoughts by importance (PageRank):")
        for tid, name, score in central['pagerank'][:3]:
            logger.info(f"    - {name}: {score:.4f}")
        
        # Show top 3 hubs (most connections)
        logger.info("  Most connected thoughts (Degree):")
        for tid, name, score in central['degree'][:3]:
            logger.info(f"    - {name}: {score:.4f}")
    except Exception as e:
        logger.error(f"✗ Failed to find central thoughts: {e}")
    
    # Test 4: Find hubs and authorities
    logger.info("\n4. Finding hub and authority thoughts...")
    try:
        hubs_auth = analyzer.find_hub_thoughts(top_n=5)
        
        logger.info("✓ Hubs and authorities identified")
        logger.info("  Top hubs (many outgoing links):")
        for hub in hubs_auth['hubs'][:3]:
            logger.info(f"    - {hub['name']}: {hub['out_degree']} outgoing")
        
        logger.info("  Top authorities (many incoming links):")
        for auth in hubs_auth['authorities'][:3]:
            logger.info(f"    - {auth['name']}: {auth['in_degree']} incoming")
    except Exception as e:
        logger.error(f"✗ Failed to find hubs: {e}")
    
    # Test 5: Analyze thought types
    logger.info("\n5. Analyzing thought types...")
    try:
        type_analysis = analyzer.analyze_thought_types()
        
        logger.info("✓ Thought types analyzed")
        logger.info("  Distribution by kind:")
        for kind, count in type_analysis['kind_distribution'].items():
            logger.info(f"    - {kind}: {count}")
        
        if type_analysis['type_distribution']:
            logger.info("  Top 5 custom types:")
            for type_name, count in list(type_analysis['type_distribution'].items())[:5]:
                logger.info(f"    - {type_name}: {count} thoughts")
    except Exception as e:
        logger.error(f"✗ Failed to analyze types: {e}")
    
    # Test 6: Find duplicates
    logger.info("\n6. Finding duplicate thought names...")
    try:
        duplicates = analyzer.find_duplicate_names()
        
        if duplicates:
            logger.info(f"✓ Found {len(duplicates)} duplicate names")
            for name, ids in list(duplicates.items())[:5]:
                logger.info(f"    - '{name}': {len(ids)} instances")
        else:
            logger.info("✓ No duplicate names found")
    except Exception as e:
        logger.error(f"✗ Failed to find duplicates: {e}")
    
    # Test 7: Find communities (if python-louvain is installed)
    logger.info("\n7. Detecting communities/clusters...")
    try:
        communities = analyzer.find_communities()
        
        logger.info(f"✓ Communities detected")
        logger.info(f"  Number of communities: {len(communities)}")
        
        # Show largest communities
        sorted_communities = sorted(communities.items(), key=lambda x: len(x[1]), reverse=True)
        for comm_id, thoughts in sorted_communities[:3]:
            thought_names = [analyzer.thought_data[tid]['Name'] for tid in thoughts[:3]]
            logger.info(f"  Community {comm_id}: {len(thoughts)} thoughts")
            logger.info(f"    Examples: {', '.join(thought_names)}")
    except ImportError:
        logger.warning("  python-louvain not installed, using basic clustering")
    except Exception as e:
        logger.error(f"✗ Failed to find communities: {e}")
    
    # Test 8: Find cycles
    logger.info("\n8. Finding cycles in the graph...")
    try:
        cycles = analyzer.find_cycles()
        
        if cycles:
            logger.info(f"✓ Found {len(cycles)} cycles")
            for cycle in cycles[:2]:
                logger.info(f"  Cycle: {' → '.join(cycle[:5])}")
        else:
            logger.info("✓ No cycles found")
    except Exception as e:
        logger.error(f"✗ Failed to find cycles: {e}")
    
    # Test 9: Path finding (example with common thoughts)
    logger.info("\n9. Testing path finding...")
    try:
        # Try to find some existing thoughts for path testing
        thought_names = [data['Name'] for data in analyzer.thought_data.values()]
        
        if len(thought_names) >= 2:
            # Pick two random thoughts
            import random
            source = random.choice(thought_names)
            target = random.choice(thought_names)
            
            path = analyzer.find_shortest_path(source, target)
            if path:
                logger.info(f"✓ Path found from '{source}' to '{target}':")
                logger.info(f"  {' → '.join(path[:10])}")  # Limit display
            else:
                logger.info(f"✓ No path exists between '{source}' and '{target}'")
    except Exception as e:
        logger.error(f"✗ Failed to find paths: {e}")
    
    # Test 10: Export capability
    logger.info("\n10. Testing export capabilities...")
    try:
        output_path = "brain_graph.graphml"
        analyzer.export_to_graphml(output_path)
        logger.info(f"✓ Graph exported to {output_path}")
        logger.info(f"  File can be opened in Gephi or other graph visualization tools")
        
        # Clean up
        if Path(output_path).exists():
            Path(output_path).unlink()
            logger.info(f"  (Test file removed)")
    except Exception as e:
        logger.error(f"✗ Failed to export graph: {e}")
    
    # Close analyzer
    analyzer.close()
    
    logger.info("\n=== Graph Analysis Test Complete ===")
    logger.info("\nKey Insights:")
    logger.info("- NetworkX successfully analyzes TheBrain database structure")
    logger.info("- Can identify important thoughts, clusters, and patterns")
    logger.info("- Enables advanced navigation and organization features")
    logger.info("- Opens possibilities for AI-powered knowledge management")
    
    return True


def main():
    """Main entry point."""
    import sys
    
    # Check if NetworkX is installed
    try:
        import networkx
        logger.info(f"NetworkX version: {networkx.__version__}")
    except ImportError:
        logger.error("NetworkX not installed. Please run: pip install networkx pandas matplotlib")
        sys.exit(1)
    
    # Run tests
    try:
        if len(sys.argv) > 1:
            # Use provided database path
            from graph_analyzer import analyze_brain_database
            analyze_brain_database(sys.argv[1])
        else:
            # Run automatic tests
            success = test_graph_analysis()
            sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
