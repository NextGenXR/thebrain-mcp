# TheBrain MCP

A **Python client library** for the TheBrain API with local SQLite caching and incremental sync. Use it from any Python project or from a host app (e.g. a desktop connector) that exposes TheBrain via MCP or similar.

## Install

### With UV (recommended)

[UV](https://docs.astral.sh/uv/) is a fast Python package manager. Use it for installs and editable mode.

**Editable install (development)** — changes in the repo are picked up without reinstalling:

```bash
# From the repo root
cd /path/to/thebrain-mcp
uv pip install -e .

# Or from another directory (use absolute path)
uv pip install -e /path/to/thebrain-mcp
```

**Normal install** — fixed copy:

```bash
uv pip install -e /path/to/thebrain-mcp   # still editable
# or
uv pip install .                          # from inside repo
# or when published:
uv pip install thebrain-mcp
```

### With pip

```bash
# Editable (development)
pip install -e /path/to/thebrain-mcp

# Normal
pip install /path/to/thebrain-mcp
# or
pip install thebrain-mcp
```

### Add to another project (e.g. Spock)

To use this library from another repo (e.g. a connector host):

1. **Clone this repo** (or add as submodule):
   ```bash
   git clone https://github.com/your-org/thebrain-mcp.git
   ```

2. **Editable install with UV** (recommended for development):
   ```bash
   cd /path/to/your-project
   uv pip install -e /path/to/thebrain-mcp
   ```
   Your app’s environment will see `thebrain_mcp`; edits in `thebrain-mcp` apply immediately.

3. **In your project’s dependency file** (e.g. `pyproject.toml`), you can reference it as:
   ```toml
   [project.optional-dependencies]
   thebrain = ["thebrain-mcp>=0.2.0"]
   ```
   For local editable use, install that extra and then override with:
   ```bash
   uv pip install -e /path/to/thebrain-mcp
   ```

4. **Use in code**:
   ```python
   from thebrain_mcp import TheBrainAPIClient, BrainCache, BrainSyncEngine, MetricsCollector
   ```

See [INSTALL.md](INSTALL.md) for step-by-step UV setup, editable install, and adding this library to another project (e.g. a desktop connector app).

## Quick use

```python
from thebrain_mcp import TheBrainAPIClient, BrainCache, BrainSyncEngine, MetricsCollector

client = TheBrainAPIClient(api_key="...")
cache = BrainCache("/path/to/cache.db")
await cache.open()
engine = BrainSyncEngine(client=client, cache=cache, metrics=MetricsCollector())
await engine.run_full_sync(brain_id)
```

## Recommended MCP tool surface

When exposing TheBrain via MCP, prefer **outcome-oriented tools** instead of many CRUD wrappers:

| Tool | Purpose |
|------|---------|
| `explore_thought` | Thought + graph + notes + attachments in one call |
| `search_brain` | Hybrid local FTS + API search |
| `create_thought` | Create with optional links, notes, type, tags |
| `update_thought` | Update properties, notes, links |
| `connect_thoughts` | Create/update link between two thoughts |
| `manage_notes` | Get, create, update, append notes |
| `manage_attachments` | List, add, get attachments |
| `analyze_graph` | Stats, centrality, communities, paths, gaps |
| `sync_brain` | Trigger sync, get status and metrics |
| `browse_brain` | List brains, get/set active, types, tags |
| `get_modifications` | Recent changes with filtering |
| `delete_entities` | Delete thought/link/attachment (with confirmation) |

## MCP resources (read-only)

- `brain://stats` — brain statistics  
- `brain://types` — thought types  
- `brain://tags` — tags  
- `brain://pins` — pinned thoughts  
- `brain://sync-status` — last sync time, cache stats, metrics  

## MCP prompts (templates)

- `summarize-neighborhood` — Summarize the knowledge neighborhood of thought X  
- `find-path` — Find and explain the path between X and Y  
- `analyze-gaps` — Identify knowledge gaps in brain X  
- `compare-thoughts` — Compare thoughts X and Y  
- `daily-digest` — Summarize today's modifications  

---

## API key and env

Create a `.env` (or set env vars) with:

```bash
THEBRAIN_API_KEY=your_api_key_here
THEBRAIN_DEFAULT_BRAIN_ID=optional_default_brain_id
```

Get an API key from [TheBrain app](https://app.thebrain.com/api-keys).

---

## What’s in this repo

- **Library only** — no MCP server. A host app (desktop connector, CLI, or server) can depend on this package and expose tools/resources.
- **Node.js** — removed; use the Python package.
- **TheBrain API** — https://api.bra.in

## License

MIT — see [LICENSE](LICENSE).
