# TheBrain MCP Technical Context

## Architecture Overview

### Core Components

#### 1. API Client (`src/api_client.py`)
- Handles all HTTP communication with TheBrain cloud API
- Manages authentication via API key
- Implements retry logic and error handling
- Base URL: `https://api.thebrain.com/v1/`

#### 2. Hybrid Brain Manager (`src/hybrid_brain_manager.py`)
- **Local Mode**: Direct SQLite database access for reads
- **Cloud Mode**: API calls for writes to maintain sync
- **Intelligent Routing**: Automatically selects optimal path
- **Caching**: In-memory caches for managers and DB paths

#### 3. Request Handlers (`src/handlers/`)
- `thoughts.py`: Core thought operations (CRUD, search, navigation)
- `links.py`: Link management between thoughts
- `notes.py`: Note content handling with markdown formatting
- `attachments.py`: File attachment operations
- `stats.py`: Brain statistics and analytics
- `hybrid_search.py`: Enhanced search with local DB support

#### 4. Tool Schemas (`src/tool_schemas.py`)
- Defines MCP tool interfaces
- Maps tool names to handler functions
- Provides parameter validation schemas
- Currently exposes 20+ tools

## Data Flow

### Read Operations
```
Claude → MCP Tool Request → Handler → Hybrid Manager → Local DB (if available)
                                    ↓
                                    → API Client → TheBrain Cloud (fallback)
```

### Write Operations
```
Claude → MCP Tool Request → Handler → API Client → TheBrain Cloud
                                    ↓
                                    → Update Local Cache
```

## Database Schema (Local SQLite)

### Core Tables
- **Thoughts**: Id, Name, Label, Kind, BrainId, timestamps
- **Links**: Id, ThoughtIdA, ThoughtIdB, Direction, Meaning
- **Tags**: Id, Name, BrainId
- **ThoughtTags**: Junction table for many-to-many
- **Notes**: ThoughtId, Content, Format
- **Attachments**: Id, ThoughtId, Name, Location
- **Types**: Id, Name, BrainId, SuperTypeId

### Indexes (Lazy Creation)
- Thoughts: Name, BrainId, TypeId, ModificationDateTime
- Links: ThoughtIdA, ThoughtIdB
- Tags: Name
- ThoughtTags: ThoughtId, TagId

## Performance Optimizations

### Caching Strategy
1. **Manager Cache**: Reuse HybridBrainManager instances
2. **DB Path Cache**: Remember brain→database mappings
3. **Lazy Indexing**: Create indexes only when needed
4. **Connection Pooling**: Reuse SQLite connections

### Query Optimizations
- Use LIMIT 1 for existence checks
- Batch operations where possible
- Indexed searches on common fields
- Avoid full table scans

## Error Handling

### Fallback Hierarchy
1. Try hybrid (local) approach first
2. Fall back to cloud API on failure
3. Return clear error with recovery hints
4. Never cause infinite recursion

### Timeout Management
- 5-second timeout for hybrid searches
- 2-second timeout for DB connections
- Configurable retry counts for API calls

## Security Considerations

### API Key Management
- Stored in environment variable `THEBRAIN_API_KEY`
- Never logged or exposed in responses
- Validated before operations begin

### Database Access
- Read-only access to user's local Brain databases
- No modification of original Brain files
- Separate cache database for MCP use

## Known Limitations

### API Limitations
- Search API doesn't always return thought IDs
- Tag operations limited to read-only
- Some bulk operations not supported

### Local Database Limitations
- Requires TheBrain desktop installation
- Database format may change between versions
- Initial indexing can be slow for large brains

## Configuration

### Environment Variables
- `THEBRAIN_API_KEY`: Required for API access
- `THEBRAIN_DISABLE_HYBRID`: Set to "true" to force API-only mode
- `THEBRAIN_LOG_LEVEL`: Control logging verbosity

### File Locations
- Windows: `%USERPROFILE%\Brains\`
- macOS: `~/Brains/`
- Linux: `~/.thebrain/`
- Cache: `~/.thebrain_mcp/databases/`

## Development Patterns

### Async/Await Throughout
- All handlers are async functions
- Database operations use asyncio
- Parallel operations where beneficial

### Consistent Response Format
```python
{
    "success": bool,
    "data": {...},      # On success
    "error": str,       # On failure
    "note": str         # Optional context
}
```

### Logging Strategy
- INFO: Normal operations
- WARNING: Fallbacks and retries
- ERROR: Failures requiring attention
- DEBUG: Detailed troubleshooting info
