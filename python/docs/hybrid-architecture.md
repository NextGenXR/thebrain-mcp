# Hybrid Local/Cloud Architecture for TheBrain MCP

## Overview

The hybrid architecture solves the limitations of TheBrain's API by using:
- **Local SQLite database** for comprehensive read operations
- **Cloud API** for write operations to maintain synchronization
- **Automatic sync** to keep local data current

## Architecture Benefits

### 1. Complete Data Access
- All thought IDs are available (no placeholders)
- Tag associations actually work
- Full-text search in notes
- Type hierarchies accessible
- Relationship graph complete

### 2. Performance
- Sub-millisecond local queries
- No API rate limiting for reads
- Batch operations possible
- Complex queries supported

### 3. Reliability
- Works offline for reads
- Fallback to API if local unavailable
- Incremental sync reduces bandwidth

## Key Components

### HybridBrainManager (`src/hybrid_brain_manager.py`)
Central manager that:
- Finds or creates local database
- Downloads brain data from cloud
- Indexes data for efficient queries
- Routes reads to local, writes to cloud
- Handles synchronization

### Enhanced Search Handlers (`src/handlers/hybrid_search.py`)
New handlers that provide:
- `search_thoughts_hybrid` - Full-featured search with tags, types, notes
- `get_tagged_thoughts` - Actually returns thoughts with specific tags
- `sync_brain_data` - Manual sync trigger
- `get_brain_statistics` - Comprehensive brain analytics
- `get_thought_graph_hybrid` - Complete relationship data

## Usage Examples

### 1. Tag-Based Search (Finally Works!)
```python
# Search for thoughts tagged with "Mega"
result = await search_thoughts_hybrid(api, {
    "brainId": "your-brain-id",
    "queryText": "tag:Mega"
})
# Returns actual thoughts with IDs, not placeholders!
```

### 2. Type-Based Search
```python
# Find all thoughts of type "Project"
result = await search_thoughts_hybrid(api, {
    "brainId": "your-brain-id",
    "queryText": "type:Project"
})
```

### 3. Recent Modifications
```python
# Get thoughts modified in last 7 days
result = await search_thoughts_hybrid(api, {
    "brainId": "your-brain-id",
    "queryText": "recent:7"
})
```

### 4. Full-Text Search in Notes
```python
# Search in note content
result = await search_thoughts_hybrid(api, {
    "brainId": "your-brain-id",
    "queryText": "Project Mega documentation",
    "searchInNotes": true
})
```

### 5. Get Tagged Thoughts
```python
# Direct tag query
result = await get_tagged_thoughts(api, {
    "brainId": "your-brain-id",
    "tagName": "Mega"
})
```

## Database Schema

The local database mirrors TheBrain's structure:

### Core Tables
- **Thoughts** - All thoughts with metadata
- **Links** - Connections between thoughts
- **Tags** - Available tags
- **ThoughtTags** - Tag associations (junction table)
- **Types** - Thought types/categories
- **Notes** - Note content for thoughts
- **Attachments** - File/URL attachments

### Indexes for Performance
- Name searches
- Tag lookups
- Type filtering
- Recent modifications
- Relationship traversal

## Sync Strategy

### Initial Setup
1. Check for existing local database
2. If not found, download from cloud
3. Create indexes for efficient queries
4. Cache manager for reuse

### Incremental Sync
1. Track last modification time
2. Query cloud for changes since then
3. Update only modified items
4. Maintain consistency

### Write Operations
1. Always write through API first
2. Update local database on success
3. Handle conflicts gracefully

## Implementation Status

✅ **Completed:**
- Hybrid brain manager core
- Local database operations
- Cloud download and indexing
- Enhanced search handlers
- Tag search functionality
- Type-based filtering
- Recent modifications tracking
- Full-text note search
- Tool schema updates
- Handler routing

🔄 **Future Enhancements:**
- Background auto-sync
- Conflict resolution
- Offline write queue
- Database compression
- Multi-brain support
- Export capabilities

## Migration Guide

### For Users
No changes needed! The hybrid features are automatically available:
- Use `search_thoughts_hybrid` for better search
- Use `get_tagged_thoughts` for tag queries
- Call `sync_brain_data` to update local data

### For Developers
The hybrid system is transparent:
```python
# Old way (limited)
results = await search_thoughts(api, {"queryText": "tag:Mega"})
# Returns empty or placeholders

# New way (complete)
results = await search_thoughts_hybrid(api, {"queryText": "tag:Mega"})
# Returns actual thoughts with IDs!
```

## Troubleshooting

### Database Not Found
- System will automatically download from cloud
- First sync may take a few minutes
- Check `~/.thebrain_mcp/databases/` for local files

### Sync Issues
- Use `sync_brain_data` with `forceDownload: true` to rebuild
- Check network connectivity
- Verify API credentials

### Performance
- Indexes are created automatically
- Large brains (10k+ thoughts) may need optimization
- Consider periodic vacuum of SQLite database

## Conclusion

The hybrid architecture provides the best of both worlds:
- **Fast, complete reads** from local database
- **Reliable writes** through cloud API
- **Automatic synchronization** for consistency

This solves the major limitations of TheBrain's API while maintaining compatibility with the cloud service.
