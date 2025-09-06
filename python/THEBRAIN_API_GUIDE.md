# TheBrain API Integration Guide

## Overview

This guide documents the quirks, patterns, and best practices for working with TheBrain API based on real-world integration experience. TheBrain API has several non-obvious behaviors that require special handling.

## Table of Contents

1. [API Response Structures](#api-response-structures)
2. [Search Functionality](#search-functionality)
3. [Graph Navigation](#graph-navigation)
4. [Common Issues and Solutions](#common-issues-and-solutions)
5. [Best Practices](#best-practices)

## API Response Structures

### Brain Structure
```python
{
    "id": "brain-uuid",
    "name": "Brain Name",
    "homeThoughtId": "thought-uuid",  # Starting point for navigation
    "description": "optional",
    "createdDateTime": "ISO-8601",
    "modifiedDateTime": "ISO-8601"
}
```

### Thought Structure
```python
{
    "id": "thought-uuid",
    "brainId": "brain-uuid",
    "name": "Thought Name",
    "label": null,  # Often null, not widely used
    "kind": 1,  # Thought type indicator
    "acType": 0,  # Access control type
    "creationDateTime": "ISO-8601",
    "modificationDateTime": "ISO-8601",
    "cleanedUpName": "thought-name"  # Normalized name
}
```

### Graph Response Structure

**IMPORTANT**: The graph API returns a different structure than documented!

```python
# Actual structure returned:
{
    "activeThought": {...},  # NOT "centralThought"
    "parents": [...],        # Direct at root, NOT under "connectedThoughts"
    "children": [...],       # Direct at root
    "jumps": [...],          # Direct at root
    "siblings": [...],       # Only if includeSiblings=true
    "tags": [...],
    "links": [...],
    "attachments": [...]
}
```

## Search Functionality

### Search Result Types

TheBrain search returns mixed results with different entity types:

```python
# Search result structure
{
    "searchResultType": 1-4,  # 1=Thought, 3=Link?, 4=Attachment
    "entityType": 1-4,         # 2=Thought, 4=Attachment
    "name": "Result Name",
    "id": "uuid",              # May be missing!
    "thoughtId": "uuid",       # May be missing!
    "attachmentId": "uuid",    # For attachments
    "sourceType": 1-2,         # 1=File, 2=URL (for attachments)
    "brainId": "uuid",
    "brainName": "Brain Name"
}
```

### Search Behavior Issues

1. **Exact Name Search Doesn't Work**: Setting `onlySearchThoughtNames=true` often returns 0 results even for exact matches
2. **Missing IDs**: Thoughts found by search (entityType=2) often lack ID fields
3. **Attachment-Heavy Results**: Most searches return attachments (PDFs, URLs) rather than thoughts
4. **Case Sensitivity**: Search appears to be case-insensitive but exact matches still fail

### Search Workarounds

```python
async def search_thoughts_enhanced(api, brain_id, query, only_names=False):
    """Enhanced search with fallback strategies."""
    
    # Try standard search
    results = await api.search_thoughts(
        brain_id, query, max_results=30, only_search_thought_names=only_names
    )
    
    # Separate thoughts from attachments
    thoughts = []
    attachments = []
    
    for result in results:
        entity_type = result.get("entityType")
        result_type = result.get("searchResultType")
        
        if result_type == 4 or entity_type == 4:
            # This is an attachment
            attachments.append(result)
        elif entity_type == 2 or result_type == 1:
            # This is a thought (but may lack ID!)
            thought_id = result.get("id") or result.get("thoughtId")
            if not thought_id and result.get("name"):
                # Create placeholder for name-only results
                thought_id = f"name:{result.get('name')}"
            thoughts.append(result)
    
    # If no thoughts found and searching by name, try graph navigation
    if len(thoughts) == 0 and only_names:
        found = await find_via_graph(api, brain_id, query)
        if found:
            thoughts.append(found)
    
    return thoughts, attachments
```

## Graph Navigation

### Traversing the Thought Graph

Since search is unreliable for exact names, graph navigation is often necessary:

```python
async def find_thought_by_name(api, brain_id, name, start_thought_id=None):
    """Find a thought by exact name using graph traversal."""
    
    # Start from home thought if not specified
    if not start_thought_id:
        brain = await api.get_brain(brain_id)
        start_thought_id = brain.get("homeThoughtId")
    
    # Get the graph
    graph = await api.get_thought_graph(brain_id, start_thought_id, False)
    
    # Check active thought (note: NOT "centralThought")
    active = graph.get("activeThought", {})
    if active.get("name") == name:
        return active
    
    # Check all connections (at root level, not nested)
    for conn_type in ["parents", "children", "jumps"]:
        for thought in graph.get(conn_type, []):
            if thought.get("name") == name:
                return thought
    
    return None
```

### Graph Structure Corrections

When processing graph data, remember:

1. Use `activeThought` not `centralThought`
2. Connections are at root level, not under `connectedThoughts`
3. Always ensure both `id` and `thoughtId` fields are present for compatibility

## Common Issues and Solutions

### Issue 1: Search Returns No Thoughts

**Problem**: Searching for known thought names returns empty results.

**Solution**: 
- Use graph navigation as fallback
- Search with broader terms and filter results
- Don't rely on `onlySearchThoughtNames=true`

### Issue 2: Thoughts Without IDs

**Problem**: Search results include thoughts without ID fields.

**Solution**:
```python
# Generate placeholder IDs for name-only results
if not thought_id and thought_name:
    thought_id = f"name:{thought_name}"
    # Flag that this needs ID lookup via graph
    needs_id_lookup = True
```

### Issue 3: Graph API Structure Mismatch

**Problem**: Documentation shows different structure than actual API returns.

**Solution**: Always use the actual structure:
```python
# Correct field names
central = graph.get("activeThought")  # NOT centralThought
parents = graph.get("parents")        # NOT connectedThoughts.parents
```

### Issue 4: Attachment-Dominated Search

**Problem**: Searches mostly return file attachments, not thoughts.

**Solution**:
- Always separate thoughts from attachments in results
- Provide both arrays to consumers
- Use entityType to distinguish (2=thought, 4=attachment)

## Best Practices

### 1. Always Handle Both ID Fields

```python
# Ensure compatibility
if "id" in thought:
    thought["thoughtId"] = thought.get("thoughtId", thought["id"])
elif "thoughtId" in thought:
    thought["id"] = thought["thoughtId"]
```

### 2. Implement Search Fallbacks

```python
# Try search first, then graph navigation
results = await search_api(query)
if not results and is_exact_name:
    result = await search_graph(query)
```

### 3. Separate Result Types

```python
return {
    "thoughts": thoughts_list,      # Actual thoughts with IDs
    "attachments": attachments_list, # Files and URLs
    "thoughtCount": len(thoughts_list),
    "attachmentCount": len(attachments_list),
    "note": "Use 'thoughts' array for items with thought IDs"
}
```

### 4. Log and Handle Edge Cases

```python
# Log unexpected result types for debugging
if not recognized_type:
    log(f"Unknown result: type={result_type}, entity={entity_type}")
```

### 5. Validate Graph Responses

```python
# Handle both old and new API structures
central = graph.get("activeThought") or graph.get("centralThought", {})
connections = graph.get("connectedThoughts", {})
parents = connections.get("parents", graph.get("parents", []))
```

## API Endpoints Reference

### Core Endpoints

- `GET /brains` - List all brains
- `GET /brains/{brainId}` - Get brain details
- `GET /thoughts/{brainId}/{thoughtId}` - Get thought details
- `GET /thoughts/{brainId}/{thoughtId}/graph` - Get thought with connections
- `GET /search/{brainId}?queryText=...` - Search (unreliable for exact names)
- `POST /thoughts/{brainId}` - Create thought
- `PATCH /thoughts/{brainId}/{thoughtId}` - Update thought (JSON Patch format)
- `DELETE /thoughts/{brainId}/{thoughtId}` - Delete thought

### Parameters

- `includeSiblings` - Include sibling thoughts in graph (default: false)
- `onlySearchThoughtNames` - Search only in thought names (often returns nothing)
- `maxResults` - Limit search results (default: 30)

## Testing Strategies

### 1. Test Search Reliability

```python
# Test with known thought name from graph
graph = await api.get_thought_graph(brain_id, home_id)
known_name = graph["children"][0]["name"]
search_results = await api.search_thoughts(brain_id, known_name)
# Often returns 0 results even with exact match!
```

### 2. Verify Graph Structure

```python
# Always check actual structure
graph = await api.get_thought_graph(...)
assert "activeThought" in graph  # Not "centralThought"
assert "parents" in graph        # At root level
```

### 3. Test Entity Types

```python
# Verify entity type handling
results = await api.search_thoughts(brain_id, "test")
for r in results:
    if r.get("entityType") == 2:
        assert "name" in r  # Thought should have name
    elif r.get("entityType") == 4:
        assert "attachmentId" in r  # Attachment should have ID
```

## Conclusion

TheBrain API requires careful handling due to:
- Inconsistent search behavior
- Missing IDs in search results
- Documentation mismatches with actual responses
- Mixed result types (thoughts vs attachments)

The key to reliable integration is implementing multiple fallback strategies and never assuming the API will behave as documented. Always test with real data and be prepared to handle edge cases.

## Change Log

- **2024-01**: Initial integration, discovered search API limitations
- **2024-01**: Added graph navigation fallback for name searches
- **2024-01**: Fixed graph structure parsing (activeThought vs centralThought)
- **2024-01**: Improved separation of thoughts and attachments in search results
