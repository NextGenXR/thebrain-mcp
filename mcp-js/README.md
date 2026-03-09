# TheBrain MCP Server (JavaScript)

Legacy Node.js MCP server for TheBrain. Preserved for reference.

The canonical connector is the **Python MCP server** in the repo root under `python/`. Install it with:

```bash
pip install -e ./python
# or from repo root:
pip install -e ./python
```

Then run the connector with:

```bash
thebrain-mcp
```

## This folder

- `index.js` – MCP server entry point
- `src/` – API client, tool schemas, handlers
- `test-*.js` – ad-hoc tests (run from this directory: `node test-format.js`, etc.)

Requires Node 18+, `THEBRAIN_API_KEY` in env or `.env`. See root [README](../README.md) and [INSTALL](../INSTALL.md).
