# TheBrain Local Database Structure Guide

## Overview

TheBrain stores a complete SQLite database locally at `C:\Users\{username}\Brains\U{XX}\B{XX}\Brain.db`. This database contains all thoughts, links, attachments, and modification history for offline access and fast performance.

## Database Schema

### Core Tables

| Table | Records | Purpose |
|-------|---------|---------|
| **Thoughts** | 1,548 | All thoughts with metadata |
| **Links** | 1,825 | Connections between thoughts |
| **Attachments** | 872 | Files and URLs attached to thoughts |
| **ModificationLogs** | 10,930 | Change history for sync |
| **BrainSettings** | - | Brain configuration |
| **TypeDefinitions** | - | Custom thought types |

### Thoughts Table Structure

```sql
CREATE TABLE Thoughts (
    Id              VARCHAR(36) PRIMARY KEY,  -- UUID
    Name            VARCHAR(140),             -- Display name
    Label           VARCHAR(140),             -- Additional label
    Kind            INTEGER,                  -- 1=Normal, 2=Type, 4=Event, 5=Gate
    ACType          INTEGER,                  -- 0=Public, 1=Private
    TypeId          VARCHAR(36),              -- Reference to type thought
    BrainId         VARCHAR(36),              -- Parent brain UUID
    
    -- DateTime fields (stored as .NET ticks)
    CreationDateTime         BIGINT,
    ModificationDateTime     BIGINT,
    ActivationDateTime       BIGINT,
    LinksModificationDateTime BIGINT,
    ForgottenDateTime        BIGINT,
    
    -- Visual properties (currently unused by API)
    ForegroundColor INTEGER,
    BackgroundColor INTEGER,
    ThoughtIconInfo VARCHAR(140),  -- Custom format: "1::0:False:False:0:"
    
    -- Sync fields
    SyncUpdateId       VARCHAR(36),
    SyncSentId         VARCHAR(36),
    SyncUpdateDateTime BIGINT
);
```

### Links Table Structure

```sql
CREATE TABLE Links (
    Id              VARCHAR(36) PRIMARY KEY,
    ThoughtIdA      VARCHAR(36),  -- Source thought
    ThoughtIdB      VARCHAR(36),  -- Target thought
    Direction       INTEGER,       -- -1=bidirectional, 0=A→B, 1=B→A
    Kind            INTEGER,       -- 1=Normal, 2=SuperParent
    Meaning         INTEGER,       -- 1=Child, 2=Parent, 3=Jump
    Relation        INTEGER,       -- Relationship type
    
    -- Visual properties
    Color           INTEGER,
    Thickness       INTEGER,
    
    -- Metadata
    Name            VARCHAR(140),
    TypeId          VARCHAR(36),
    CreationDateTime BIGINT,
    ModificationDateTime BIGINT
);
```

## Key Data Patterns

### 1. DateTime Format

All DateTime fields use **.NET ticks** (100-nanosecond intervals since 1/1/0001):

```python
def convert_ticks_to_datetime(ticks):
    """Convert .NET ticks to Python datetime."""
    # .NET epoch: January 1, 0001
    # Unix epoch: January 1, 1970
    # Difference: 621355968000000000 ticks
    
    TICKS_PER_SECOND = 10_000_000
    EPOCH_DIFFERENCE = 621355968000000000
    
    unix_ticks = ticks - EPOCH_DIFFERENCE
    unix_seconds = unix_ticks / TICKS_PER_SECOND
    
    return datetime.fromtimestamp(unix_seconds)

# Example: 638127703902707196 → 2023-02-26 12:46:30
```

### 2. Thought Kinds

| Kind | Type | Count | Description |
|------|------|-------|-------------|
| 1 | Normal | 1,465 | Regular thoughts |
| 2 | Type | 29 | Thought types (categories) |
| 4 | Event | 53 | Calendar/time-based thoughts |
| 5 | Gate | 1 | Special gate thoughts |

### 3. Type Hierarchy

Thoughts can have **types** that are other thoughts:

```
TypeId → Points to another thought that acts as a type
Example: "Beau Perschall" has TypeId → "Dev Team" thought
```

Your brain has custom types like:
- Component (10 thoughts)
- Dev Team (3 thoughts)
- Jira INITIATIVE (3 thoughts)
- Jira MOTIF (15 thoughts)
- Priority Highest (1 thought)

### 4. Link Meanings

| Meaning | Type | Description |
|---------|------|-------------|
| 1 | Child | Parent-child relationship |
| 2 | Parent | Reverse of child |
| 3 | Jump | Non-hierarchical connection |

### 5. ThoughtIconInfo Format

Custom icon data stored as delimited string (not JSON):
```
"1::0:False:False:0:"
 │  │ │     │     └─ Unknown flag
 │  │ │     └─────── Boolean flag
 │  │ └───────────── Boolean flag  
 │  └─────────────── Icon index
 └────────────────── Icon type
```

## Special Handling Requirements

### 1. DateTime Conversion

```python
class BrainDateTimeHandler:
    @staticmethod
    def from_ticks(ticks):
        if not ticks:
            return None
        # Handle .NET ticks format
        return datetime.fromtimestamp((ticks - 621355968000000000) / 10000000)
    
    @staticmethod
    def to_ticks(dt):
        if not dt:
            return None
        # Convert to .NET ticks
        return int(dt.timestamp() * 10000000) + 621355968000000000
```

### 2. Special Characters in Names

Names can contain:
- Ampersands: `Media & Entertainment`
- Parentheses: `DGPT Data Governance & Privacy Team (Formerly DPT)`
- Apostrophes: `NVIDIA's Cloud Function`
- Unicode characters

**No HTML encoding needed** - stored as plain text.

### 3. Orphaned Thoughts

39 thoughts have **no links** (orphaned). Handle gracefully:

```python
def get_thought_connections(thought_id):
    # Check if thought has any links
    links = query("""
        SELECT * FROM Links 
        WHERE ThoughtIdA = ? OR ThoughtIdB = ?
    """, (thought_id, thought_id))
    
    if not links:
        # Orphaned thought - may still be valid
        return {"orphaned": True, "connections": []}
```

### 4. File System Structure

Each thought may have a folder with attachments:

```
C:\Users\{user}\Brains\U01\B02\
├── Brain.db                              # Main database
├── {thought-uuid}\                       # Thought folder
│   ├── Notes.md                         # Markdown notes
│   └── {attachment-uuid}.{ext}          # Attached files
```

### 5. Incremental Sync via ModificationLogs

Use ModificationLogs for tracking changes:

```python
def get_recent_changes(since_datetime):
    """Get thoughts modified since a specific time."""
    since_ticks = datetime_to_ticks(since_datetime)
    
    return query("""
        SELECT DISTINCT t.* 
        FROM Thoughts t
        JOIN ModificationLogs m ON t.Id = m.ExtraAId
        WHERE m.CreationDateTime > ?
        ORDER BY m.CreationDateTime DESC
    """, (since_ticks,))
```

## Performance Optimizations

### 1. Create Indexes for Fast Search

```sql
-- Add indexes for common queries
CREATE INDEX IF NOT EXISTS idx_thoughts_name ON Thoughts(Name);
CREATE INDEX IF NOT EXISTS idx_thoughts_type ON Thoughts(TypeId);
CREATE INDEX IF NOT EXISTS idx_links_thoughta ON Links(ThoughtIdA);
CREATE INDEX IF NOT EXISTS idx_links_thoughtb ON Links(ThoughtIdB);
CREATE INDEX IF NOT EXISTS idx_mods_datetime ON ModificationLogs(CreationDateTime);
```

### 2. Batch Loading Strategy

```python
def load_brain_optimized(db_path):
    """Load entire brain into memory for fast access."""
    
    # Load all thoughts in one query
    thoughts = query("SELECT * FROM Thoughts")
    thought_map = {t['Id']: t for t in thoughts}
    
    # Load all links
    links = query("SELECT * FROM Links")
    
    # Build connection graph
    for link in links:
        add_connection(thought_map, link)
    
    return thought_map
```

### 3. Cache Note Content

```python
class NoteCache:
    def __init__(self, brain_path):
        self.brain_path = Path(brain_path)
        self.cache = {}
    
    def get_note(self, thought_id):
        if thought_id not in self.cache:
            note_path = self.brain_path / thought_id / "Notes.md"
            if note_path.exists():
                self.cache[thought_id] = note_path.read_text(encoding='utf-8')
            else:
                self.cache[thought_id] = None
        return self.cache[thought_id]
```

## Security Considerations

1. **Read-Only Access**: Only read from local DB, write through API
2. **Path Validation**: Validate all file paths before access
3. **SQL Injection**: Use parameterized queries only
4. **File Permissions**: Check read permissions before accessing

## Integration with MCP Server

### Hybrid Approach

```python
class HybridThoughtProvider:
    def __init__(self, api_client, local_db_path):
        self.api = api_client
        self.local_db = LocalBrainCache(local_db_path)
        
    async def search(self, query):
        # 1. Try local DB first (instant)
        local_results = self.local_db.search(query)
        if local_results:
            return local_results
            
        # 2. Fall back to API if needed
        return await self.api.search(query)
    
    async def update(self, thought_id, changes):
        # Always write through API for cloud sync
        result = await self.api.update(thought_id, changes)
        
        # Update local cache
        self.local_db.refresh_thought(thought_id)
        
        return result
```

## Summary

The local Brain database provides:

✅ **Complete offline access** to all 1,548 thoughts  
✅ **Instant search** without API calls  
✅ **Full relationship graph** via Links table  
✅ **Change tracking** via ModificationLogs  
✅ **Direct note access** from filesystem  

Key challenges:
- DateTime conversion from .NET ticks
- Type hierarchy relationships
- Orphaned thoughts handling
- Incremental sync strategy

With proper handling of these patterns, the local database enables sub-millisecond searches and complete offline functionality while maintaining sync with the cloud via the API for writes.
