# TheBrain MCP System Patterns

## Design Patterns

### 1. Hybrid Read/Write Pattern
**Intent**: Optimize performance by reading from local, writing to cloud
```python
async def operation(brain_id, data):
    # Reads: Use local database
    result = await manager.read_from_local(brain_id)
    
    # Writes: Use cloud API
    await api.write_to_cloud(brain_id, data)
    
    # Update local cache
    await manager.update_local_cache(data)
```

### 2. Graceful Degradation Pattern
**Intent**: Ensure functionality even when optimal path fails
```python
try:
    # Try optimal path (hybrid/local)
    result = await hybrid_search(query)
except Exception:
    # Fall back to basic path (API)
    result = await api_search(query)
    # Add note about degraded mode
    result["note"] = "Using fallback mode"
```

### 3. Manager Singleton Pattern
**Intent**: Reuse expensive resources across requests
```python
_manager_cache = {}

async def get_or_create_manager(brain_id):
    if brain_id not in _manager_cache:
        _manager_cache[brain_id] = await create_manager(brain_id)
    return _manager_cache[brain_id]
```

### 4. Lazy Initialization Pattern
**Intent**: Defer expensive operations until needed
```python
class HybridBrainManager:
    def __init__(self):
        self.is_indexed = False
    
    async def search(self):
        if not self.is_indexed:
            await self._create_indexes()  # Only when first needed
        return await self._perform_search()
```

## Coding Conventions

### Naming Conventions
- **Functions**: `snake_case` (e.g., `search_thoughts`)
- **Classes**: `PascalCase` (e.g., `HybridBrainManager`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RESULTS`)
- **Private methods**: `_leading_underscore` (e.g., `_verify_brain_id`)
- **Tool names**: `snake_case` (e.g., `get_thought_graph`)

### Response Structures
```python
# Success Response
{
    "success": True,
    "data": {...},           # Primary data
    "count": int,            # If collection
    "note": "Optional info"  # User-friendly context
}

# Error Response
{
    "success": False,
    "error": "Error message",
    "fallbackNote": "Recovery suggestion"
}
```

### Error Handling Rules
1. **Catch specific exceptions** - Never use bare `except:`
2. **Log before returning** - Use appropriate log level
3. **Provide recovery hints** - Tell user what to try next
4. **Preserve stack traces** - Include in debug logs
5. **Never swallow errors** - Always report failures

### Async Patterns
```python
# Parallel operations
results = await asyncio.gather(
    operation1(),
    operation2(),
    operation3()
)

# Timeout protection
result = await asyncio.wait_for(
    slow_operation(),
    timeout=5.0
)

# Background tasks
task = asyncio.create_task(sync_operation())
# Don't await if fire-and-forget
```

## Database Patterns

### Query Optimization
```python
# Good: Use LIMIT for existence checks
cursor.execute("SELECT 1 FROM Table WHERE id = ? LIMIT 1", (id,))
exists = cursor.fetchone() is not None

# Good: Use indexes
cursor.execute("SELECT * FROM Thoughts WHERE Name LIKE ? AND BrainId = ?")

# Bad: Full table scan
cursor.execute("SELECT * FROM Thoughts")  # Avoid!
```

### Transaction Management
```python
try:
    cursor.execute("BEGIN")
    # Multiple operations
    cursor.execute("INSERT ...")
    cursor.execute("UPDATE ...")
    cursor.execute("COMMIT")
except Exception as e:
    cursor.execute("ROLLBACK")
    raise
```

## API Integration Patterns

### Retry Logic
```python
async def api_call_with_retry(func, *args, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await func(*args)
        except (timeout, ConnectionError) as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### Rate Limiting
```python
class RateLimiter:
    def __init__(self, calls_per_second=10):
        self.interval = 1.0 / calls_per_second
        self.last_call = 0
    
    async def acquire(self):
        now = time.time()
        wait_time = self.last_call + self.interval - now
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        self.last_call = time.time()
```

## Testing Patterns

### Test Structure
```python
async def test_feature():
    # Arrange
    setup_test_data()
    
    # Act
    result = await function_under_test()
    
    # Assert
    assert result["success"] == True
    assert "expected_key" in result
    
    # Cleanup
    cleanup_test_data()
```

### Mock Patterns
```python
# Mock at specific module level
@patch("src.handlers.thoughts.api_call")
async def test_with_mock(mock_api):
    mock_api.return_value = {"success": True}
    result = await handler_function()
    assert result["success"]
```

## Performance Patterns

### Caching Strategy
1. **Memory cache** for frequently accessed data
2. **Disk cache** for large datasets
3. **TTL-based invalidation** for time-sensitive data
4. **Event-based invalidation** for write operations

### Batch Processing
```python
# Process in chunks to avoid memory issues
CHUNK_SIZE = 100
for i in range(0, len(items), CHUNK_SIZE):
    chunk = items[i:i + CHUNK_SIZE]
    await process_chunk(chunk)
```

## Security Patterns

### Input Validation
```python
def validate_brain_id(brain_id: str) -> bool:
    # UUID format validation
    try:
        uuid.UUID(brain_id)
        return True
    except ValueError:
        return False
```

### Sensitive Data Handling
```python
# Never log sensitive data
logger.info(f"Connecting to brain {brain_id[:8]}...")  # Truncate IDs
# Never: logger.info(f"API key: {api_key}")  # NEVER DO THIS!
```

## Documentation Patterns

### Function Documentation
```python
async def complex_operation(
    brain_id: str,
    options: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Perform a complex operation on a brain.
    
    Args:
        brain_id: The brain identifier
        options: Configuration options including:
            - max_depth: Maximum traversal depth
            - include_notes: Whether to include notes
    
    Returns:
        Dict containing:
            - success: Operation status
            - data: Result data
            - count: Number of items processed
    
    Raises:
        ValueError: If brain_id is invalid
        ConnectionError: If API is unreachable
    """
```

### Code Comments
```python
# Use comments to explain WHY, not WHAT
# Good: Skip indexing for now - it might be slow
# Bad: Set is_indexed to False

# TODO comments with context
# TODO: Add rate limiting when API supports it

# FIXME with issue reference
# FIXME: Workaround for API bug #123
```
