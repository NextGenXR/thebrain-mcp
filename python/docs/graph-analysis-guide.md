# Graph Analysis Guide for TheBrain MCP

## Overview

TheBrain's structure is fundamentally a **directed graph** where:
- **Nodes** = Thoughts
- **Edges** = Links (Parent/Child/Jump relationships)

Using graph analysis libraries like NetworkX, we can gain powerful insights into knowledge structure, find patterns, and optimize organization.

## Why Graph Analysis?

### 1. **Understanding Structure**
- Identify central/important thoughts (hubs)
- Find isolated or orphaned thoughts
- Detect communities of related concepts
- Measure connectivity and density

### 2. **Navigation Optimization**
- Find shortest paths between concepts
- Identify missing links
- Suggest new connections
- Detect redundant paths

### 3. **Quality Improvement**
- Find duplicate thoughts
- Identify cycles and loops
- Detect structural anomalies
- Measure knowledge coverage

### 4. **Advanced Features**
- AI-powered organization suggestions
- Automatic clustering
- Knowledge gap analysis
- Relationship pattern detection

## Using the Graph Analyzer

### Basic Usage

```python
from src.graph_analyzer import BrainGraphAnalyzer

# Load your Brain database
analyzer = BrainGraphAnalyzer("C:/Users/YourName/Brains/U01/B02/Brain.db")

# Load the graph
graph = analyzer.load_graph()

# Get statistics
stats = analyzer.get_statistics()
print(f"Total thoughts: {stats['basic']['total_thoughts']}")
print(f"Orphaned thoughts: {stats['orphaned_thoughts']['count']}")
```

### Finding Important Thoughts

```python
# Find central thoughts using various algorithms
central = analyzer.find_central_thoughts(top_n=10)

# Degree centrality: Most connected thoughts
for thought_id, name, score in central['degree']:
    print(f"{name}: {score:.3f}")

# Betweenness centrality: Thoughts that bridge different areas
for thought_id, name, score in central['betweenness']:
    print(f"{name}: {score:.3f}")

# PageRank: Important thoughts (like Google's algorithm)
for thought_id, name, score in central['pagerank']:
    print(f"{name}: {score:.3f}")
```

### Finding Communities

```python
# Detect clusters of related thoughts
communities = analyzer.find_communities()

for comm_id, thought_ids in communities.items():
    thoughts = [analyzer.thought_data[tid]['Name'] for tid in thought_ids[:5]]
    print(f"Community {comm_id}: {len(thought_ids)} thoughts")
    print(f"  Examples: {', '.join(thoughts)}")
```

### Path Analysis

```python
# Find shortest path between two thoughts
path = analyzer.find_shortest_path("Machine Learning", "NVIDIA")
if path:
    print(" → ".join(path))

# Find cycles (circular references)
cycles = analyzer.find_cycles()
for cycle in cycles:
    print("Cycle found: " + " → ".join(cycle) + " → " + cycle[0])
```

### Finding Duplicates

```python
# Find thoughts with duplicate names
duplicates = analyzer.find_duplicate_names()
for name, thought_ids in duplicates.items():
    print(f"'{name}' appears {len(thought_ids)} times")
```

## Advanced Analysis Examples

### 1. Knowledge Coverage Analysis

```python
def analyze_knowledge_gaps(analyzer):
    """Find areas that might need more connections."""
    
    # Find thoughts with very few connections
    graph = analyzer.graph
    low_degree = [
        (node, analyzer.thought_data[node]['Name']) 
        for node, degree in graph.degree() 
        if degree < 2
    ]
    
    print(f"Thoughts needing more connections: {len(low_degree)}")
    
    # Find disconnected subgraphs
    components = list(nx.weakly_connected_components(graph))
    if len(components) > 1:
        print(f"Found {len(components)} disconnected knowledge islands")
    
    return low_degree, components
```

### 2. Mega Project Analysis

```python
def analyze_mega_project(analyzer):
    """Analyze the Mega project structure in your NVIDIA brain."""
    
    # Get neighborhood around Mega-tagged thoughts
    mega_neighborhood = analyzer.get_thought_neighborhood("Mega", depth=2)
    
    # Find all paths from Mega to SimReady
    paths = nx.all_simple_paths(
        analyzer.graph, 
        source="mega_thought_id",
        target="simready_thought_id",
        cutoff=5  # Max path length
    )
    
    # Analyze link types in Mega area
    mega_links = []
    for edge in mega_neighborhood.edges(data=True):
        meaning = edge[2].get('meaning', 0)
        mega_links.append(meaning)
    
    link_distribution = Counter(mega_links)
    print("Link types in Mega area:", link_distribution)
```

### 3. Temporal Analysis

```python
def analyze_recent_growth(analyzer, days=30):
    """Analyze how the brain has grown recently."""
    
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=days)
    
    recent_thoughts = []
    for tid, data in analyzer.thought_data.items():
        created = analyzer._ticks_to_datetime(data.get('CreationDateTime'))
        if created and datetime.fromisoformat(created) > cutoff:
            recent_thoughts.append((tid, data['Name'], created))
    
    print(f"Thoughts created in last {days} days: {len(recent_thoughts)}")
    
    # Analyze where growth is happening
    growth_areas = defaultdict(int)
    for tid, name, _ in recent_thoughts:
        # Find parent thoughts
        parents = list(analyzer.graph.predecessors(tid))
        for parent in parents:
            parent_name = analyzer.thought_data[parent]['Name']
            growth_areas[parent_name] += 1
    
    print("Areas of recent growth:")
    for area, count in sorted(growth_areas.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  - {area}: {count} new thoughts")
```

## Visualization Options

### 1. Export to Gephi

```python
# Export for visualization in Gephi (powerful graph viz tool)
analyzer.export_to_graphml("my_brain.graphml")
```

### 2. Simple Matplotlib Visualization

```python
import matplotlib.pyplot as plt
import networkx as nx

# Get a subgraph for visualization (full graph might be too large)
subgraph = analyzer.get_thought_neighborhood("NVIDIA", depth=2)

# Create layout
pos = nx.spring_layout(subgraph, k=2, iterations=50)

# Draw
plt.figure(figsize=(12, 8))
nx.draw(subgraph, pos, 
        with_labels=True,
        node_size=500,
        node_color='lightblue',
        font_size=8,
        arrows=True)
plt.title("NVIDIA Thought Neighborhood")
plt.show()
```

### 3. Interactive Visualization with Pyvis

```python
from pyvis.network import Network

def create_interactive_viz(analyzer, thought_name, depth=2):
    """Create an interactive HTML visualization."""
    
    # Get subgraph
    subgraph = analyzer.get_thought_neighborhood(thought_name, depth)
    
    # Create Pyvis network
    net = Network(height="750px", width="100%", directed=True)
    
    # Add nodes
    for node in subgraph.nodes():
        name = analyzer.thought_data[node]['Name']
        net.add_node(node, label=name, title=name)
    
    # Add edges
    for edge in subgraph.edges(data=True):
        meaning = {1: "Child", 2: "Parent", 3: "Jump"}.get(
            edge[2].get('meaning', 0), "Link"
        )
        net.add_edge(edge[0], edge[1], title=meaning)
    
    # Generate HTML
    net.show("brain_graph.html", notebook=False)
    print(f"Interactive graph saved to brain_graph.html")
```

## Integration with MCP Server

### Adding Graph Analysis Tools

```python
# In tool_schemas.py, add:

{
    "name": "analyze_brain_graph",
    "description": "Analyze the knowledge graph structure of a brain",
    "inputSchema": {
        "type": "object",
        "properties": {
            "brainId": {"type": "string"},
            "analysisType": {
                "type": "string",
                "enum": ["statistics", "central", "communities", "duplicates"]
            }
        },
        "required": ["brainId", "analysisType"]
    }
},

{
    "name": "find_knowledge_paths",
    "description": "Find paths between two thoughts",
    "inputSchema": {
        "type": "object",
        "properties": {
            "brainId": {"type": "string"},
            "sourceThought": {"type": "string"},
            "targetThought": {"type": "string"},
            "maxLength": {"type": "integer", "default": 5}
        },
        "required": ["brainId", "sourceThought", "targetThought"]
    }
}
```

## Performance Considerations

### Large Brains (10K+ thoughts)

1. **Use sampling for analysis**:
```python
# Sample a random subgraph for quick analysis
sampled_nodes = random.sample(list(graph.nodes()), min(1000, len(graph)))
subgraph = graph.subgraph(sampled_nodes)
```

2. **Cache analysis results**:
```python
# Store expensive computations
import pickle

# Save
with open('centrality_cache.pkl', 'wb') as f:
    pickle.dump(central_thoughts, f)

# Load
with open('centrality_cache.pkl', 'rb') as f:
    central_thoughts = pickle.load(f)
```

3. **Use approximate algorithms**:
```python
# Approximate betweenness centrality (much faster)
approx_between = nx.betweenness_centrality(
    graph, 
    k=100  # Sample 100 nodes instead of all
)
```

## Benefits for Your Workflow

### For the Mega Project
- Map all Mega-related thoughts and their connections
- Find which concepts bridge Mega and SimReady
- Identify knowledge gaps in the Mega documentation
- Track project growth over time

### For NVIDIA Brain Organization
- Identify the most important/central concepts
- Find and merge duplicate entries
- Discover hidden connections between projects
- Optimize navigation paths

### For AI Integration
- Better context for Claude when navigating
- Automatic suggestion of related thoughts
- Smart search based on graph distance
- Predictive linking suggestions

## Next Steps

1. **Install Requirements**:
```bash
pip install networkx pandas matplotlib
# Optional but recommended:
pip install python-louvain pyvis plotly
```

2. **Run Analysis**:
```bash
python src/graph_analyzer.py "C:/Users/joconnor/Brains/U01/B02/Brain.db"
```

3. **Integrate with MCP**:
- Add graph analysis handlers
- Create visualization endpoints
- Build automated organization tools

The graph analysis capabilities transform TheBrain from a static knowledge base into a dynamic, analyzable knowledge graph that can provide insights, detect patterns, and suggest improvements!
