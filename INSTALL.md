# Installation and integration

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

Spock is a desktop app that can load a “connector” which uses this library to talk to TheBrain. The connector lives in the Spock repo (or its `ext/` submodule), not in this repo.

### 1. Install thebrain-mcp in Spock’s environment (editable)

From your host app (e.g. Spock) or connector repo:

```bash
cd /path/to/your-host-app
# or the subfolder where your connector lives, e.g. ext/connectors

# Create/use a venv, then:
uv pip install -e /path/to/thebrain-mcp
```

Replace `/path/to/thebrain-mcp` with the real path (e.g. `G:\GitHub\thebrain-mcp` or `~/GitHub/thebrain-mcp`).

### 2. Declare the dependency (optional)

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
| Work on thebrain-mcp and run tests | `cd thebrain-mcp && uv sync --extra dev && uv run pytest tests/` |
| Use thebrain-mcp from another project (editable) | `uv pip install -e /path/to/thebrain-mcp` |
| Use thebrain-mcp from Spock (editable) | From Spock repo: `uv pip install -e /path/to/thebrain-mcp` |
