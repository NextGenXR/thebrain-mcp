# Local Database Setup for Hybrid Mode

## Where TheBrain Stores Its Databases

TheBrain stores its local databases in a specific directory structure:

### Windows (Default Location)
```
C:\Users\[YourUsername]\Brains\
├── U00\
│   └── User.db    # First brain database
├── U01\
│   └── User.db    # Second brain database
└── device.info    # Device metadata
```

### Other Possible Locations
- **Windows Alternative**: `%USERPROFILE%\Documents\TheBrain\`
- **macOS**: `~/Library/Application Support/TheBrain/`
- **Linux**: `~/.thebrain/` or `~/.local/share/thebrain/`

## How the Hybrid System Finds Your Brain

The system uses a smart discovery process:

1. **Automatic Discovery**
   - First checks `~/Brains/` directory (TheBrain's standard location)
   - Scans each subdirectory (U00, U01, etc.) for `User.db` files
   - Verifies which database contains the requested brain ID

2. **Multi-Brain Support**
   - If you have multiple brains, the system checks each one
   - Automatically selects the correct database for your brain ID
   - No manual configuration needed!

3. **Fallback to Download**
   - Only downloads from cloud if brain not found locally
   - Saves bandwidth and time by reusing existing data

## Directory Structure Explained

```
%USERPROFILE%\Brains\
├── U00\                    # First brain slot
│   ├── User.db            # SQLite database with all brain data
│   ├── Notes\             # Note content files
│   ├── Attachments\       # Attached files
│   └── ...
├── U01\                    # Second brain slot
│   ├── User.db            # Another brain's database
│   └── ...
└── device.info            # Device configuration
```

## Verifying Your Setup

To check if your brain will be found automatically:

1. **Check Directory Exists**
   ```powershell
   Test-Path "$env:USERPROFILE\Brains"
   ```

2. **List Available Brains**
   ```powershell
   Get-ChildItem "$env:USERPROFILE\Brains" -Directory
   ```

3. **Verify Database Files**
   ```powershell
   Get-ChildItem "$env:USERPROFILE\Brains\*\User.db"
   ```

## Manual Configuration (Optional)

If your Brain databases are in a non-standard location, you can:

1. **Set Environment Variable**
   ```powershell
   $env:THEBRAIN_DB_PATH = "C:\CustomPath\YourBrain.db"
   ```

2. **Pass Path Directly**
   ```python
   manager = HybridBrainManager(api_client, local_db_path="C:\CustomPath\YourBrain.db")
   ```

## Troubleshooting

### Brain Not Found
If the system can't find your brain:
1. Verify TheBrain is installed and has been run at least once
2. Check that `User.db` exists in one of the U0x subdirectories
3. Ensure the brain ID matches what's in the database

### Multiple Brains
The system automatically handles multiple brains:
- Checks each U0x directory sequentially
- Finds the correct database based on brain ID
- No manual selection needed

### Performance Tips
- First access to a brain may take a moment to verify
- Subsequent accesses are instant (cached)
- The system creates indexes automatically for fast queries

## Benefits of Using Local Database

1. **Speed**: Millisecond queries vs seconds for API calls
2. **Complete Access**: All thought IDs, tags, and relationships
3. **Offline Capability**: Works without internet after initial setup
4. **No API Limits**: Unlimited local queries
5. **Privacy**: Data stays on your machine

## Example Usage

When you use the hybrid search functions, the system automatically:

```python
# This automatically finds your brain in C:\Users\[YourName]\Brains\
result = search_thoughts_hybrid({
    "brainId": "your-brain-id",
    "queryText": "tag:Mega"
})

# The system:
# 1. Checks C:\Users\[YourName]\Brains\U00\User.db
# 2. If not there, checks U01\User.db, etc.
# 3. Finds the right brain and uses it
# 4. Returns complete results with all IDs!
```

No configuration needed - it just works!
