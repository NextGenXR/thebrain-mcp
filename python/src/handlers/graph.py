"""
Graph analysis handlers for TheBrain MCP server.

Provides graph-based insights and analysis of knowledge structure.
"""

from typing import Dict, Any, List, Optional
import logging
from pathlib import Path
from ..graph_analyzer import BrainGraphAnalyzer
from ..hybrid_brain_manager import HybridBrainManager
from ..path_utils import find_brain_database, get_brain_path_from_env

logger = logging.getLogger(__name__)

# Cache for graph analyzers
_analyzer_cache: Dict[str, BrainGraphAnalyzer] = {}


async def get_or_create_analyzer(api, brain_id: str) -> Optional[BrainGraphAnalyzer]:
    """Get or create a graph analyzer for a brain."""
    if brain_id in _analyzer_cache:
        return _analyzer_cache[brain_id]
    
    # Try to get local database path from hybrid manager
    try:
        from ..handlers.hybrid_search import get_or_create_manager
        manager = await get_or_create_manager(api, brain_id)
        
        if manager and manager.local_db_path:
            analyzer = BrainGraphAnalyzer(manager.local_db_path)
            # Don't filter by brain_id - local DB contains all thoughts
            graph = analyzer.load_graph()
            if graph.number_of_nodes() > 0:
                _analyzer_cache[brain_id] = analyzer
                logger.info(f"Loaded graph via hybrid manager: {graph.number_of_nodes()} nodes from {manager.local_db_path}")
                return analyzer
            else:
                logger.warning(f"Graph loaded but has no nodes from {manager.local_db_path}")
    except Exception as e:
        logger.warning(f"Could not create analyzer from hybrid manager: {e}")
    
    # Try to find database using our path utilities
    try:
        # First check environment variable
        custom_path = get_brain_path_from_env()
        db_path = find_brain_database(custom_path=str(custom_path) if custom_path else None)
        
        if db_path:
            try:
                analyzer = BrainGraphAnalyzer(str(db_path))
                # Don't filter by brain_id for local database - it contains all data
                graph = analyzer.load_graph()  # Load all thoughts
                if graph.number_of_nodes() > 0:
                    _analyzer_cache[brain_id] = analyzer
                    logger.info(f"Loaded graph from {db_path}: {graph.number_of_nodes()} nodes")
                    return analyzer
                else:
                    logger.warning(f"Graph loaded but has no nodes from {db_path}")
            except Exception as e:
                logger.error(f"Failed to load graph from {db_path}: {e}")
        else:
            logger.warning("Could not find Brain database in any standard location")
    except Exception as e:
        logger.error(f"Error in path finding: {e}")
    
    return None


async def analyze_brain_graph(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the knowledge graph structure of a brain.
    
    Provides statistics, centrality measures, and structural insights.
    """
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        analysis_type = args.get("analysisType", "statistics")
        
        analyzer = await get_or_create_analyzer(api, brain_id)
        if not analyzer:
            return {
                "success": False,
                "error": "Could not access local database. Please ensure TheBrain.exe is running and your database is synced. Check that THEBRAIN_LOCAL_DB_PATH is set correctly in your .env file or that your database is in the default location (~/Brains)."
            }
        
        if analysis_type == "statistics":
            stats = analyzer.get_statistics()
            return {
                "success": True,
                "statistics": stats,
                "graphInfo": {
                    "nodes": analyzer.graph.number_of_nodes(),
                    "edges": analyzer.graph.number_of_edges(),
                    "density": stats['basic']['density']
                }
            }
        
        elif analysis_type == "central":
            central = analyzer.find_central_thoughts(top_n=10)
            return {
                "success": True,
                "centralThoughts": {
                    measure: [
                        {"id": tid, "name": name, "score": score}
                        for tid, name, score in thoughts
                    ]
                    for measure, thoughts in central.items()
                }
            }
        
        elif analysis_type == "communities":
            communities = analyzer.find_communities()
            # Format communities for response
            formatted = {}
            for comm_id, thought_ids in communities.items():
                thoughts = []
                for tid in thought_ids[:20]:  # Limit to 20 per community
                    if tid in analyzer.thought_data:
                        thoughts.append({
                            "id": tid,
                            "name": analyzer.thought_data[tid]['Name']
                        })
                formatted[str(comm_id)] = {
                    "size": len(thought_ids),
                    "thoughts": thoughts
                }
            
            return {
                "success": True,
                "communities": formatted,
                "totalCommunities": len(communities)
            }
        
        elif analysis_type == "duplicates":
            duplicates = analyzer.find_duplicate_names()
            formatted = []
            for name, ids in duplicates.items():
                formatted.append({
                    "name": name,
                    "count": len(ids),
                    "thoughtIds": ids
                })
            
            return {
                "success": True,
                "duplicates": formatted,
                "totalDuplicates": len(duplicates)
            }
        
        elif analysis_type == "orphans":
            import networkx as nx
            isolates = list(nx.isolates(analyzer.graph))
            orphans = []
            for tid in isolates[:50]:  # Limit to 50
                if tid in analyzer.thought_data:
                    orphans.append({
                        "id": tid,
                        "name": analyzer.thought_data[tid]['Name']
                    })
            
            return {
                "success": True,
                "orphanedThoughts": orphans,
                "totalOrphans": len(isolates)
            }
        
        elif analysis_type == "hubs":
            hubs_auth = analyzer.find_hub_thoughts(top_n=10)
            return {
                "success": True,
                "hubs": hubs_auth['hubs'],
                "authorities": hubs_auth['authorities']
            }
        
        else:
            return {
                "success": False,
                "error": f"Unknown analysis type: {analysis_type}"
            }
        
    except Exception as e:
        logger.error(f"Graph analysis error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def find_knowledge_paths(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Find paths between two thoughts in the knowledge graph.
    
    Useful for understanding how concepts are related.
    """
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        source_thought = args["sourceThought"]
        target_thought = args["targetThought"]
        max_length = args.get("maxLength", 5)
        
        analyzer = await get_or_create_analyzer(api, brain_id)
        if not analyzer:
            return {
                "success": False,
                "error": "Could not access local database. Please ensure TheBrain.exe is running and your database is synced. Check that THEBRAIN_LOCAL_DB_PATH is set correctly in your .env file or that your database is in the default location (~/Brains)."
            }
        
        # Find shortest path
        path = analyzer.find_shortest_path(source_thought, target_thought)
        
        if path:
            return {
                "success": True,
                "shortestPath": path,
                "pathLength": len(path) - 1,
                "sourceThought": source_thought,
                "targetThought": target_thought
            }
        else:
            return {
                "success": True,
                "shortestPath": None,
                "message": f"No path found between '{source_thought}' and '{target_thought}'",
                "sourceThought": source_thought,
                "targetThought": target_thought
            }
        
    except Exception as e:
        logger.error(f"Path finding error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_thought_neighborhood(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get the neighborhood of a thought up to a specified depth.
    
    Returns all connected thoughts within the specified distance.
    """
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        thought_name = args["thoughtName"]
        depth = args.get("depth", 2)
        
        analyzer = await get_or_create_analyzer(api, brain_id)
        if not analyzer:
            return {
                "success": False,
                "error": "Could not access local database. Please ensure TheBrain.exe is running and your database is synced. Check that THEBRAIN_LOCAL_DB_PATH is set correctly in your .env file or that your database is in the default location (~/Brains)."
            }
        
        # Get neighborhood subgraph
        subgraph = analyzer.get_thought_neighborhood(thought_name, depth)
        
        # Format results
        thoughts = []
        links = []
        
        for node_id in subgraph.nodes():
            if node_id in analyzer.thought_data:
                thoughts.append({
                    "id": node_id,
                    "name": analyzer.thought_data[node_id]['Name']
                })
        
        for edge in subgraph.edges(data=True):
            links.append({
                "source": edge[0],
                "target": edge[1],
                "meaning": edge[2].get('meaning', 0)
            })
        
        return {
            "success": True,
            "centerThought": thought_name,
            "depth": depth,
            "thoughts": thoughts,
            "links": links,
            "thoughtCount": len(thoughts),
            "linkCount": len(links)
        }
        
    except Exception as e:
        logger.error(f"Neighborhood analysis error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def find_knowledge_gaps(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Find areas in the knowledge graph that might need more connections.
    
    Identifies isolated clusters, low-connectivity areas, and missing links.
    """
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        min_connections = args.get("minConnections", 2)
        
        analyzer = await get_or_create_analyzer(api, brain_id)
        if not analyzer:
            return {
                "success": False,
                "error": "Could not access local database. Please ensure TheBrain.exe is running and your database is synced. Check that THEBRAIN_LOCAL_DB_PATH is set correctly in your .env file or that your database is in the default location (~/Brains)."
            }
        
        import networkx as nx
        
        # Find low-degree thoughts
        low_degree = []
        for node, degree in analyzer.graph.degree():
            if degree < min_connections:
                if node in analyzer.thought_data:
                    low_degree.append({
                        "id": node,
                        "name": analyzer.thought_data[node]['Name'],
                        "connections": degree
                    })
        
        # Find disconnected components
        components = list(nx.weakly_connected_components(analyzer.graph))
        disconnected = []
        if len(components) > 1:
            # Skip the largest component (main graph)
            sorted_components = sorted(components, key=len, reverse=True)
            for comp in sorted_components[1:6]:  # Show up to 5 islands
                island_thoughts = []
                for tid in list(comp)[:10]:  # Show up to 10 thoughts per island
                    if tid in analyzer.thought_data:
                        island_thoughts.append({
                            "id": tid,
                            "name": analyzer.thought_data[tid]['Name']
                        })
                disconnected.append({
                    "size": len(comp),
                    "thoughts": island_thoughts
                })
        
        # Find potential missing links (thoughts with similar names but no connection)
        potential_links = []
        thought_names = {}
        for tid, data in analyzer.thought_data.items():
            name = data['Name'].lower()
            if name not in thought_names:
                thought_names[name] = []
            thought_names[name].append((tid, data['Name']))
        
        # Look for similar names
        for base_name, thoughts in thought_names.items():
            if len(thoughts) > 1:
                # Check if these similar thoughts are connected
                for i, (tid1, name1) in enumerate(thoughts):
                    for tid2, name2 in thoughts[i+1:]:
                        if not analyzer.graph.has_edge(tid1, tid2) and not analyzer.graph.has_edge(tid2, tid1):
                            potential_links.append({
                                "thought1": {"id": tid1, "name": name1},
                                "thought2": {"id": tid2, "name": name2},
                                "reason": "Similar names but not connected"
                            })
        
        return {
            "success": True,
            "knowledgeGaps": {
                "lowConnectivityThoughts": low_degree[:50],  # Limit to 50
                "disconnectedIslands": disconnected,
                "potentialMissingLinks": potential_links[:20],  # Limit to 20
                "summary": {
                    "thoughtsNeedingConnections": len(low_degree),
                    "disconnectedClusters": len(components) - 1 if len(components) > 1 else 0,
                    "suggestedLinks": len(potential_links)
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Knowledge gap analysis error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def export_graph_visualization(api, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Export the graph for visualization in external tools.
    
    Supports GraphML format for Gephi and other visualization tools.
    """
    try:
        brain_id = args.get("brainId")
        if not brain_id:
            raise ValueError("Brain ID is required")
        
        output_format = args.get("format", "graphml")
        output_path = args.get("outputPath", f"brain_{brain_id}.{output_format}")
        
        analyzer = await get_or_create_analyzer(api, brain_id)
        if not analyzer:
            return {
                "success": False,
                "error": "Could not access local database. Please ensure TheBrain.exe is running and your database is synced. Check that THEBRAIN_LOCAL_DB_PATH is set correctly in your .env file or that your database is in the default location (~/Brains)."
            }
        
        if output_format == "graphml":
            analyzer.export_to_graphml(output_path)
            
            return {
                "success": True,
                "outputPath": output_path,
                "format": "graphml",
                "nodeCount": analyzer.graph.number_of_nodes(),
                "edgeCount": analyzer.graph.number_of_edges(),
                "message": f"Graph exported to {output_path}. Open with Gephi or similar tools."
            }
        else:
            return {
                "success": False,
                "error": f"Unsupported format: {output_format}. Use 'graphml'."
            }
        
    except Exception as e:
        logger.error(f"Graph export error: {e}")
        return {
            "success": False,
            "error": str(e)
        }
