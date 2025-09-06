# Testing Graph Analysis in Claude Desktop

## Quick Setup

1. **Restart Claude Desktop** to pick up the new configuration with database path support

2. **Make sure your brain ID is set** (check with list_brains first if needed)

## Test Commands to Try

### 1. Get Overall Statistics
Ask Claude:
"Can you analyze the graph structure of my brain and show me statistics?"

This will run: `analyze_brain_graph` with `analysisType: "statistics"`

### 2. Find Most Important Thoughts
Ask Claude:
"What are the most central and important thoughts in my brain?"

This will run: `analyze_brain_graph` with `analysisType: "central"`

### 3. Find Communities
Ask Claude:
"Can you identify clusters or communities of related thoughts in my brain?"

This will run: `analyze_brain_graph` with `analysisType: "communities"`

### 4. Find Duplicate Thoughts
Ask Claude:
"Are there any duplicate thought names in my brain that I should merge?"

This will run: `analyze_brain_graph` with `analysisType: "duplicates"`

### 5. Find Orphaned Thoughts
Ask Claude:
"Can you find isolated or orphaned thoughts that have no connections?"

This will run: `analyze_brain_graph` with `analysisType: "orphans"`

### 6. Find Knowledge Paths
Ask Claude:
"How are 'Omniverse' and 'AI' connected in my brain?"

This will run: `find_knowledge_paths` with source and target thoughts

### 7. Explore Neighborhoods
Ask Claude:
"Show me all thoughts connected to 'Omniverse' within 2 steps"

This will run: `get_thought_neighborhood` with depth 2

### 8. Find Knowledge Gaps
Ask Claude:
"Can you identify areas in my brain that need more connections?"

This will run: `find_knowledge_gaps` to find isolated areas

### 9. Export for Visualization
Ask Claude:
"Can you export my brain graph for visualization in Gephi?"

This will run: `export_graph_visualization` to create a GraphML file

## Example Conversation Flow

You: "I'd like to analyze my brain structure"

Claude: "I'll analyze your brain's knowledge graph structure..."
[Runs analyze_brain_graph with statistics]

You: "Which thoughts are most important?"

Claude: "Let me find the most central thoughts..."
[Runs analyze_brain_graph with central]

You: "Are there any isolated areas I should connect?"

Claude: "I'll check for knowledge gaps..."
[Runs find_knowledge_gaps]

## Behind the Scenes

The MCP server:
1. Automatically finds your local Brain.db using the new path configuration
2. Loads it into NetworkX for graph analysis
3. Performs the requested analysis
4. Returns formatted results to Claude

## Troubleshooting

If tools aren't appearing:
1. Check Claude Desktop logs: %APPDATA%\Claude\logs\
2. Verify your .env has THEBRAIN_API_KEY set
3. Ensure Python dependencies are installed (networkx)
4. Try restarting Claude Desktop

## Performance Notes

- First analysis may take a few seconds to load the graph
- Subsequent analyses are cached for speed
- Large brains (10K+ thoughts) may need a moment for complex analyses
- Database path is automatically detected or uses your .env setting
