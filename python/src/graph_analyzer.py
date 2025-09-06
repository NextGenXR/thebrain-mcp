"""
Graph Analysis for TheBrain Database using NetworkX

This module provides advanced graph analysis capabilities for TheBrain databases,
enabling network analysis, pattern detection, and visualization of knowledge graphs.
"""

import sqlite3
import networkx as nx
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
import logging
import json
from collections import defaultdict, Counter

# Handle both module and direct script execution
try:
    from .path_utils import expand_path, find_brain_database, get_brain_path_from_env, format_path_for_display, get_default_brain_paths
except ImportError:
    from path_utils import expand_path, find_brain_database, get_brain_path_from_env, format_path_for_display, get_default_brain_paths

logger = logging.getLogger(__name__)


class BrainGraphAnalyzer:
    """
    Analyze TheBrain database as a network graph using NetworkX.
    
    Provides insights into:
    - Graph structure and connectivity
    - Clustering and communities
    - Central/important thoughts
    - Paths and relationships
    - Orphaned or isolated thoughts
    """
    
    def __init__(self, db_path: str):
        """
        Initialize with path to Brain.db file.
        
        Args:
            db_path: Path to Brain.db file (supports environment variables and ~)
        """
        # Expand path if it contains environment variables or ~
        if db_path:
            db_path = str(expand_path(db_path))
        self.db_path = db_path
        
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Brain database not found at {format_path_for_display(Path(db_path))}")
            
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.graph = None
        self.thought_data = {}
        self.link_data = {}
        
    def load_graph(self, brain_id: Optional[str] = None) -> nx.DiGraph:
        """
        Load the brain into a NetworkX directed graph.
        
        Returns:
            NetworkX DiGraph with thoughts as nodes and links as edges
        """
        self.graph = nx.DiGraph()
        cursor = self.conn.cursor()
        
        # Load all thoughts as nodes
        query = "SELECT * FROM Thoughts"
        params = []
        if brain_id:
            query += " WHERE BrainId = ?"
            params.append(brain_id)
            
        cursor.execute(query, params)
        
        for row in cursor.fetchall():
            thought = dict(row)
            thought_id = thought['Id']
            
            # Store full thought data
            self.thought_data[thought_id] = thought
            
            # Add node with key attributes
            self.graph.add_node(
                thought_id,
                name=thought['Name'],
                label=thought.get('Label'),
                kind=thought.get('Kind', 1),
                type_id=thought.get('TypeId'),
                created=self._ticks_to_datetime(thought.get('CreationDateTime')),
                modified=self._ticks_to_datetime(thought.get('ModificationDateTime')),
                forgotten=thought.get('ForgottenDateTime') is not None
            )
        
        # Load all links as edges
        cursor.execute("SELECT * FROM Links")
        
        for row in cursor.fetchall():
            link = dict(row)
            link_id = link['Id']
            
            # Store full link data
            self.link_data[link_id] = link
            
            # Determine edge direction
            source = link['ThoughtIdA']
            target = link['ThoughtIdB']
            direction = link.get('Direction', 0)
            
            # Skip if nodes don't exist (could be from different brain)
            if source not in self.graph or target not in self.graph:
                continue
            
            # Add edge with attributes
            edge_attrs = {
                'link_id': link_id,
                'meaning': link.get('Meaning', 1),  # 1=Child, 2=Parent, 3=Jump
                'kind': link.get('Kind', 1),
                'relation': link.get('Relation'),
                'name': link.get('Name'),
                'created': self._ticks_to_datetime(link.get('CreationDateTime'))
            }
            
            if direction == -1:  # Bidirectional
                self.graph.add_edge(source, target, **edge_attrs)
                self.graph.add_edge(target, source, **edge_attrs)
            elif direction == 0:  # A→B
                self.graph.add_edge(source, target, **edge_attrs)
            else:  # B→A
                self.graph.add_edge(target, source, **edge_attrs)
        
        logger.info(f"Loaded graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
        return self.graph
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive graph statistics."""
        if not self.graph:
            self.load_graph()
        
        stats = {
            'basic': {
                'total_thoughts': self.graph.number_of_nodes(),
                'total_links': self.graph.number_of_edges(),
                'density': nx.density(self.graph),
                'is_connected': nx.is_weakly_connected(self.graph),
            },
            'connectivity': {
                'weakly_connected_components': nx.number_weakly_connected_components(self.graph),
                'strongly_connected_components': nx.number_strongly_connected_components(self.graph),
                'average_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes() if self.graph.number_of_nodes() > 0 else 0,
            }
        }
        
        # Find isolates (orphaned thoughts)
        isolates = list(nx.isolates(self.graph))
        stats['orphaned_thoughts'] = {
            'count': len(isolates),
            'thoughts': [self.thought_data[i]['Name'] for i in isolates[:10]]  # First 10
        }
        
        # Degree distribution
        degrees = dict(self.graph.degree())
        stats['degree_distribution'] = {
            'max_degree': max(degrees.values()) if degrees else 0,
            'min_degree': min(degrees.values()) if degrees else 0,
            'avg_degree': sum(degrees.values()) / len(degrees) if degrees else 0
        }
        
        return stats
    
    def find_central_thoughts(self, top_n: int = 10) -> List[Tuple[str, str, float]]:
        """
        Find the most central/important thoughts using various centrality measures.
        
        Returns:
            List of (thought_id, thought_name, centrality_score) tuples
        """
        if not self.graph:
            self.load_graph()
        
        centrality_measures = {
            'degree': nx.degree_centrality(self.graph),
            'betweenness': nx.betweenness_centrality(self.graph),
            'closeness': nx.closeness_centrality(self.graph),
        }
        
        # PageRank requires scipy, so make it optional
        try:
            centrality_measures['pagerank'] = nx.pagerank(self.graph)
        except ImportError:
            logger.warning("scipy not installed, skipping PageRank calculation")
        
        results = {}
        for measure_name, scores in centrality_measures.items():
            top_thoughts = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
            results[measure_name] = [
                (tid, self.thought_data[tid]['Name'], score)
                for tid, score in top_thoughts
            ]
        
        return results
    
    def find_communities(self) -> Dict[int, List[str]]:
        """
        Detect communities/clusters of related thoughts.
        
        Returns:
            Dictionary mapping community ID to list of thought IDs
        """
        if not self.graph:
            self.load_graph()
        
        # Convert to undirected for community detection
        undirected = self.graph.to_undirected()
        
        # Use Louvain community detection
        try:
            import community as community_louvain
            communities = community_louvain.best_partition(undirected)
            
            # Organize by community
            community_map = defaultdict(list)
            for thought_id, comm_id in communities.items():
                community_map[comm_id].append(thought_id)
            
            return dict(community_map)
        except ImportError:
            # Fallback to connected components
            logger.warning("python-louvain not installed, using connected components")
            components = nx.weakly_connected_components(self.graph)
            return {i: list(comp) for i, comp in enumerate(components)}
    
    def find_shortest_path(self, source_name: str, target_name: str) -> Optional[List[str]]:
        """
        Find shortest path between two thoughts by name.
        
        Returns:
            List of thought names in the path, or None if no path exists
        """
        if not self.graph:
            self.load_graph()
        
        # Find thoughts by name
        source_id = None
        target_id = None
        
        for tid, data in self.thought_data.items():
            if data['Name'] == source_name:
                source_id = tid
            if data['Name'] == target_name:
                target_id = tid
        
        if not source_id or not target_id:
            return None
        
        try:
            path_ids = nx.shortest_path(self.graph, source_id, target_id)
            return [self.thought_data[tid]['Name'] for tid in path_ids]
        except nx.NetworkXNoPath:
            return None
    
    def find_cycles(self) -> List[List[str]]:
        """Find cycles in the thought graph."""
        if not self.graph:
            self.load_graph()
        
        cycles = list(nx.simple_cycles(self.graph))
        return [
            [self.thought_data[tid]['Name'] for tid in cycle]
            for cycle in cycles[:10]  # Limit to first 10 cycles
        ]
    
    def analyze_thought_types(self) -> Dict[str, Any]:
        """Analyze distribution of thought types and their relationships."""
        if not self.graph:
            self.load_graph()
        
        # Count by Kind
        kind_counts = Counter()
        type_counts = Counter()
        
        for node_id in self.graph.nodes():
            thought = self.thought_data[node_id]
            kind = thought.get('Kind', 1)
            type_id = thought.get('TypeId')
            
            kind_name = {
                1: 'Normal',
                2: 'Type',
                4: 'Event',
                5: 'Gate'
            }.get(kind, f'Unknown({kind})')
            
            kind_counts[kind_name] += 1
            
            if type_id and type_id in self.thought_data:
                type_name = self.thought_data[type_id]['Name']
                type_counts[type_name] += 1
        
        return {
            'kind_distribution': dict(kind_counts),
            'type_distribution': dict(type_counts.most_common(20)),  # Top 20 types
        }
    
    def find_hub_thoughts(self, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Find hub thoughts (high out-degree) and authority thoughts (high in-degree).
        """
        if not self.graph:
            self.load_graph()
        
        in_degrees = dict(self.graph.in_degree())
        out_degrees = dict(self.graph.out_degree())
        
        # Top hubs (many outgoing links)
        hubs = sorted(out_degrees.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        # Top authorities (many incoming links)
        authorities = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        return {
            'hubs': [
                {
                    'name': self.thought_data[tid]['Name'],
                    'out_degree': degree,
                    'id': tid
                }
                for tid, degree in hubs
            ],
            'authorities': [
                {
                    'name': self.thought_data[tid]['Name'],
                    'in_degree': degree,
                    'id': tid
                }
                for tid, degree in authorities
            ]
        }
    
    def get_thought_neighborhood(self, thought_name: str, depth: int = 2) -> nx.DiGraph:
        """
        Get subgraph of a thought and its neighbors up to specified depth.
        
        Returns:
            NetworkX subgraph containing the neighborhood
        """
        if not self.graph:
            self.load_graph()
        
        # Find thought by name
        thought_id = None
        for tid, data in self.thought_data.items():
            if data['Name'] == thought_name:
                thought_id = tid
                break
        
        if not thought_id:
            return nx.DiGraph()
        
        # Get all nodes within depth
        nodes = {thought_id}
        for _ in range(depth):
            new_nodes = set()
            for node in nodes:
                new_nodes.update(self.graph.predecessors(node))
                new_nodes.update(self.graph.successors(node))
            nodes.update(new_nodes)
        
        # Return subgraph
        return self.graph.subgraph(nodes).copy()
    
    def find_duplicate_names(self) -> Dict[str, List[str]]:
        """Find thoughts with duplicate names."""
        name_map = defaultdict(list)
        
        for tid, data in self.thought_data.items():
            name = data['Name']
            if name:
                name_map[name].append(tid)
        
        # Return only duplicates
        return {
            name: ids 
            for name, ids in name_map.items() 
            if len(ids) > 1
        }
    
    def export_to_graphml(self, output_path: str):
        """Export graph to GraphML format for visualization in tools like Gephi."""
        if not self.graph:
            self.load_graph()
        
        # Add thought names as labels for visualization
        for node_id in self.graph.nodes():
            self.graph.nodes[node_id]['label'] = self.thought_data[node_id]['Name']
        
        nx.write_graphml(self.graph, output_path)
        logger.info(f"Exported graph to {output_path}")
    
    def _ticks_to_datetime(self, ticks: Optional[int]) -> Optional[str]:
        """Convert .NET ticks to ISO datetime string."""
        if not ticks:
            return None
        try:
            unix_timestamp = (ticks - 621355968000000000) / 10000000
            return datetime.fromtimestamp(unix_timestamp).isoformat()
        except:
            return None
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


# Example usage and analysis functions
def analyze_brain_database(db_path: str):
    """
    Perform comprehensive analysis of a Brain database.
    
    Args:
        db_path: Path to Brain.db file
    """
    analyzer = BrainGraphAnalyzer(db_path)
    
    # Load the graph
    graph = analyzer.load_graph()
    print(f"\n=== Brain Graph Loaded ===")
    print(f"Thoughts: {graph.number_of_nodes()}")
    print(f"Links: {graph.number_of_edges()}")
    
    # Get statistics
    stats = analyzer.get_statistics()
    print(f"\n=== Graph Statistics ===")
    print(f"Density: {stats['basic']['density']:.4f}")
    print(f"Connected: {stats['basic']['is_connected']}")
    print(f"Orphaned thoughts: {stats['orphaned_thoughts']['count']}")
    print(f"Average degree: {stats['degree_distribution']['avg_degree']:.2f}")
    
    # Find central thoughts
    print(f"\n=== Most Central Thoughts ===")
    central = analyzer.find_central_thoughts(5)
    for measure, thoughts in central.items():
        print(f"\n{measure.capitalize()} Centrality:")
        for tid, name, score in thoughts[:3]:
            print(f"  - {name}: {score:.4f}")
    
    # Find hubs and authorities
    hubs_auth = analyzer.find_hub_thoughts(5)
    print(f"\n=== Hub Thoughts (Many Outgoing Links) ===")
    for hub in hubs_auth['hubs'][:3]:
        print(f"  - {hub['name']}: {hub['out_degree']} outgoing")
    
    print(f"\n=== Authority Thoughts (Many Incoming Links) ===")
    for auth in hubs_auth['authorities'][:3]:
        print(f"  - {auth['name']}: {auth['in_degree']} incoming")
    
    # Analyze types
    type_analysis = analyzer.analyze_thought_types()
    print(f"\n=== Thought Type Distribution ===")
    for kind, count in type_analysis['kind_distribution'].items():
        print(f"  - {kind}: {count}")
    
    # Find duplicates
    duplicates = analyzer.find_duplicate_names()
    if duplicates:
        print(f"\n=== Duplicate Names Found ===")
        for name, ids in list(duplicates.items())[:5]:
            print(f"  - '{name}': {len(ids)} instances")
    
    # Find communities
    communities = analyzer.find_communities()
    print(f"\n=== Communities Detected ===")
    print(f"Number of communities: {len(communities)}")
    largest = max(communities.values(), key=len)
    print(f"Largest community size: {len(largest)} thoughts")
    
    analyzer.close()
    return analyzer


if __name__ == "__main__":
    # Example: Analyze a Brain database
    import sys
    import os
    
    if len(sys.argv) > 1:
        # User provided a path - expand it
        db_path = expand_path(sys.argv[1])
    else:
        # Try to find database automatically
        # First check environment variable
        env_path = get_brain_path_from_env()
        if env_path:
            db_path = find_brain_database(custom_path=str(env_path))
        else:
            # Search in default locations
            db_path = find_brain_database()
        
        if not db_path:
            # Fallback to old default
            db_path = Path.home() / "Brains" / "U01" / "B02" / "Brain.db"
    
    if db_path and Path(db_path).exists():
        print(f"Analyzing database: {format_path_for_display(Path(db_path))}")
        analyzer = analyze_brain_database(str(db_path))
    else:
        print("Database not found. Please specify path as argument.")
        print(f"Usage: python {sys.argv[0]} [path_to_Brain.db]")
        print(f"\nSearched locations:")
        for path in get_default_brain_paths():
            print(f"  - {format_path_for_display(path)}")
        sys.exit(1)
