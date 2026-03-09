# TheBrain MCP - library image (for future standalone MCP server with streamable-http)
FROM python:3.12-slim AS base

WORKDIR /app

# Install uv for fast installs
RUN pip install --no-cache-dir uv

# Copy project and install package
COPY pyproject.toml ./
COPY src/ src/
RUN uv pip install --system . --no-cache

# Default: verify import (replace with MCP server entrypoint when added)
CMD ["python", "-c", "from thebrain_mcp import __version__; print('thebrain-mcp', __version__)"]
