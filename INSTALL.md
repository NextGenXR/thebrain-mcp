# Installation and integration

**Version:** The repo version is in the root [VERSION](VERSION) file (e.g. `0.2.0`). Both the root library and the `python/` connector use it.

## Two ways to use this repo

| What you want | Install | Result |
|---------------|---------|--------|
| **Library** (client, cache, sync, graph) in your own code | `pip install -e .` from repo root | `thebrain_mcp` package to import |
| **MCP connector** (run as server for Spock / MCP clients) | `pip install -e ./python` from repo root | `thebrain-mcp` command in PATH |

## UV and editable install (-e)

### Why editable install?

With an **editable install** (`pip install -e <path>` or `uv pip install -e <path>`), the package is linked from its source directory. Changes you make in the `thebrain-mcp` repo are used immediately by the environment that installed it — no reinstall after each edit.

### Using UV

1. **Install UV** (if needed):
   ```bash
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **From thebrain-mcp repo** (create venv and install in one go):
   ```bash
   cd /path/to/thebrain-mcp
   uv sync --extra dev
   uv run pytest tests/
   ```

3. **Editable install into another project’s environment**:
   ```bash
   cd /path/to/your-project
   uv pip install -e /path/to/thebrain-mcp
   ```
   Use an absolute path so the link stays correct when you change directories.

### Using pip

```bash
cd /path/to/your-project
pip install -e /path/to/thebrain-mcp
```

---

## Adding thebrain-mcp to Spock

Spock is a desktop app that can load a connector that uses MCP to talk to TheBrain. You can either run the MCP connector from this repo (Option A) or embed the library in your own connector (Option B).

### Option A: Run the MCP connector (pip-install the server)

Install the connector package so the `thebrain-mcp` executable is available; point Spock at it as the MCP server:

```bash
uv pip install -e /path/to/thebrain-mcp/python
thebrain-mcp
```

Configure Spock to use `thebrain-mcp` as the MCP server command.

### Option B: Use the library in your own connector

From your host app (e.g. Spock) or connector repo:

```bash
cd /path/to/your-host-app
# or the subfolder where your connector lives, e.g. ext/connectors

# Create/use a venv, then:
uv pip install -e /path/to/thebrain-mcp
```

Replace `/path/to/thebrain-mcp` with the real path (e.g. `G:\GitHub\thebrain-mcp` or `~/GitHub/thebrain-mcp`).

### 2. Declare the dependency (optional, for library use)

In the host app’s project (e.g. `pyproject.toml` in the repo that contains the connector), you can add:

```toml
[project.optional-dependencies]
thebrain = ["thebrain-mcp>=0.2.0"]
```

Then install that extra when needed. For day-to-day development, keep using the editable install so you can change thebrain-mcp without republishing.

### 3. Use in the connector

The connector code (in the Spock repo) imports the library:

```python
from thebrain_mcp import (
    TheBrainAPIClient,
    BrainCache,
    BrainSyncEngine,
    MetricsCollector,
)
```

No references to this repo’s name or to any specific host (e.g. Spock) are required inside thebrain-mcp; the host app is responsible for wiring the connector.

---

## Summary

| Goal | Command |
|------|--------|
| Version number | See root [VERSION](VERSION) (e.g. 0.2.0) |
| Work on library and run tests | `cd thebrain-mcp && uv sync --extra dev && uv run pytest tests/` |
| Install MCP connector (get `thebrain-mcp` command) | `pip install -e ./python` or `uv pip install -e /path/to/thebrain-mcp/python` |
| Use library from another project (editable) | `uv pip install -e /path/to/thebrain-mcp` |
| Use connector or library from Spock | `uv pip install -e /path/to/thebrain-mcp/python` (connector) or `.../thebrain-mcp` (library) |
