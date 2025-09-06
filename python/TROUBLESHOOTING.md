# TheBrain MCP Server Troubleshooting Guide

## Common Issues and Solutions

### 1. Claude Can't Find Thoughts by Name

**Symptom**: Claude says "The search isn't returning thought IDs" or can't find thoughts even with exact names.

**Cause**: TheBrain's search API has limitations:
- `onlySearchThoughtNames=true` often returns 0 results
- Search results frequently lack thought IDs
- Most results are attachments (files/URLs) not thoughts

**Solution**: The server now includes automatic fallbacks:
- Graph navigation when exact name search fails
- Separation of thoughts from attachments in results
- ID generation for name-only results

**What to tell Claude**: "Try searching for the thought name. If that doesn't work, try navigating from the home thought using the graph."

---

### 2. Server Won't Start

**Symptom**: Error when running the server or Claude can't connect.

**Diagnosis Steps**:

1. **Check environment variables**:
   ```bash
   # In python directory
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('THEBRAIN_API_KEY')[:10] + '...' if os.getenv('THEBRAIN_API_KEY') else 'NOT SET')"
   ```

2. **Test API connection**:
   ```bash
   uv run python test_server.py
   ```

3. **Check Claude configuration**:
   - Open `%APPDATA%\Claude\claude_desktop_config.json`
   - Verify the path to Python executable
   - Ensure `cwd` points to the `python` folder

**Common Fixes**:
- Missing `.env` file → Copy `.env.example` and add your API key
- Wrong Python path → Use full path to `.venv\Scripts\python.exe`
- Module errors → Run `uv sync` to reinstall dependencies

---

### 3. Search Returns Only Attachments

**Symptom**: Searches return PDFs, URLs, and files but no actual thoughts.

**Explanation**: TheBrain indexes attachment content heavily. Many searches will return attachments rather than thoughts.

**Workaround**:
- Look at the `thoughts` array specifically (not `results`)
- Use `onlySearchThoughtNames: true` for thought-specific searches
- Navigate using the graph from known thoughts

**Response Structure**:
```json
{
  "success": true,
  "thoughts": [...],      // Actual thoughts with IDs
  "attachments": [...],   // Files and URLs
  "thoughtCount": 0,
  "attachmentCount": 5,
  "note": "Found 0 thoughts and 5 attachments..."
}
```

---

### 4. Empty Search Results

**Symptom**: Searches return empty even for known content.

**Common Causes**:
1. Wrong brain ID being used
2. Search index not updated in TheBrain
3. API limitations with exact name matching

**Solutions**:
1. Verify brain ID:
   ```python
   # List all brains to check IDs
   result = list_brains()
   ```

2. Try broader search terms:
   - Instead of "Project Alpha", try "Alpha"
   - Instead of full names, try partial matches

3. Use graph navigation instead of search

---

### 5. Graph Navigation Returns Empty

**Symptom**: Getting thought graph returns empty connections.

**Check**:
```python
# The structure should be:
{
  "activeThought": {...},  # NOT "centralThought"
  "parents": [...],
  "children": [...],
  "jumps": [...]
}
```

**Common Issues**:
- Thought has no connections (isolated thought)
- Wrong thought ID
- Permission issues with the brain

---

### 6. API Key Issues

**Symptom**: "Unauthorized" or "Invalid API key" errors.

**Verification**:
1. Check API key format (should be UUID format)
2. Verify key in TheBrain application:
   - Open TheBrain
   - Go to Account Settings
   - Check API Access section

3. Test directly:
   ```python
   import httpx
   response = httpx.get(
       "https://api.bra.in/thoughts/v1/brains",
       headers={"Authorization": f"Bearer {api_key}"}
   )
   print(response.status_code)  # Should be 200
   ```

---

### 7. Claude Desktop Connection Issues

**Symptom**: Claude shows "Failed to connect to server" or similar.

**Debug Steps**:

1. **Check logs**:
   ```
   %APPDATA%\Claude\logs\mcp-server-thebrain.log
   ```

2. **Test server manually**:
   ```bash
   cd python
   .venv\Scripts\python.exe main.py
   ```
   Should output: "TheBrain MCP server started"

3. **Verify config format**:
   ```json
   {
     "mcpServers": {
       "thebrain": {
         "command": "C:\\Git\\thebrain-mcp\\python\\.venv\\Scripts\\python.exe",
         "args": ["C:\\Git\\thebrain-mcp\\python\\main.py"],
         "cwd": "C:\\Git\\thebrain-mcp\\python",
         "env": {}
       }
     }
   }
   ```

---

### 8. Performance Issues

**Symptom**: Slow responses or timeouts.

**Optimizations**:
1. Reduce search result limits:
   ```python
   search_thoughts(brain_id, query, max_results=10)  # Instead of 30
   ```

2. Avoid recursive graph traversal
3. Cache brain list if not changing frequently

---

## Debug Mode

To enable debug logging, edit `python/src/handlers/thoughts.py`:

```python
# Uncomment these lines:
import sys
print(f"[DEBUG] Search query: '{query_text}'", file=sys.stderr)
```

Debug output appears in:
- Terminal when running manually
- `mcp-server-thebrain.log` when running via Claude

---

## Getting Help

1. **Check the API Guide**: See `THEBRAIN_API_GUIDE.md` for detailed API behavior
2. **Review test files**: `test_server.py` and `test_api.py` for examples
3. **Enable debug logging**: See above
4. **Check TheBrain API status**: https://www.thebrain.com/

---

## Quick Fixes

### Reset Everything
```bash
cd python
# Windows
rmdir /s .venv
setup-uv.bat

# Mac/Linux  
rm -rf .venv
./setup-uv.sh
```

### Test Core Functions
```python
# Create test_core.py
import asyncio
from src.api_client import TheBrainAPI
from src import handlers

async def test():
    api = TheBrainAPI("your-api-key")
    
    # Test 1: List brains
    result = await handlers.list_brains(api)
    print(f"Brains: {result.get('count')}")
    
    # Test 2: Search
    result = await handlers.search_thoughts(api, {
        "brainId": "your-brain-id",
        "queryText": "test",
        "maxResults": 5
    })
    print(f"Results: {result.get('thoughtCount')} thoughts, {result.get('attachmentCount')} attachments")
    
    await api.close()

asyncio.run(test())
```

---

## Known Limitations

1. **Search API**: Exact name matching is unreliable
2. **No Bulk Operations**: API doesn't support batch updates
3. **Limited Filtering**: Can't filter search by thought type/tags
4. **Attachment Search**: Can't exclude attachments from search
5. **Graph Depth**: Can only get immediate connections, not full graph

These are API limitations, not bugs in the MCP server.
