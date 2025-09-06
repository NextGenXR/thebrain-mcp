# UV - Primary Dependency Management for TheBrain MCP

## Overview

This project uses **UV** as the primary tool for Python dependency management. UV is a fast, reliable Python package installer and resolver written in Rust, designed as a drop-in replacement for pip and pip-tools.

## Why UV?

- **⚡ Fast**: 10-100x faster than pip
- **🔒 Reliable**: Consistent dependency resolution
- **🎯 Simple**: Drop-in replacement for pip
- **📦 Modern**: Built with Rust for performance
- **🔄 Compatible**: Works with existing Python workflows

## Installation

### Windows (PowerShell)
```powershell
# Automatic installation
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or using our setup script
.\setup-uv.ps1
```

### macOS/Linux
```bash
# Automatic installation
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using our setup script
./setup-uv.sh
```

## Quick Start

### 1. Create Virtual Environment
```bash
uv venv
```

### 2. Install Dependencies
```bash
# Install all dependencies from pyproject.toml
uv pip install -e .

# Install with optional visualization tools
uv pip install -e ".[visualization]"
```

### 3. Run the Server
```bash
# Using UV directly (recommended)
uv run python main.py

# Or activate venv first
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
python main.py
```

## Development Workflow

### Adding Dependencies

1. **Add to pyproject.toml**:
```toml
dependencies = [
    "new-package>=1.0.0",
]
```

2. **Sync dependencies**:
```bash
uv pip sync
```

### Installing Dev Dependencies

UV recognizes the `[tool.uv]` section in pyproject.toml:
```bash
# Install dev dependencies
uv pip install -e ".[dev]"
```

### Updating Dependencies

```bash
# Update all dependencies
uv pip install --upgrade -e .

# Update specific package
uv pip install --upgrade networkx
```

### Freezing Dependencies

```bash
# Generate lock file
uv pip freeze > requirements-lock.txt
```

## Project Structure

```
python/
├── pyproject.toml        # Primary dependency configuration
├── uv.lock              # UV lock file (auto-generated)
├── setup-uv.ps1         # Windows UV setup script
├── setup-uv.sh          # Unix UV setup script
├── run-uv.bat           # Windows UV run script  
└── run-uv.sh            # Unix UV run script
```

## UV Commands Reference

### Basic Commands
```bash
# Create virtual environment
uv venv

# Install from pyproject.toml
uv pip install -e .

# Install specific package
uv pip install pandas

# Uninstall package
uv pip uninstall pandas

# List installed packages
uv pip list

# Show package info
uv pip show networkx
```

### Advanced Commands
```bash
# Compile dependencies
uv pip compile pyproject.toml -o requirements.txt

# Sync exact dependencies
uv pip sync requirements.txt

# Install with specific Python version
uv venv --python 3.11
uv pip install -e .
```

## Integration with Claude Desktop

The Claude Desktop configuration uses UV-managed Python:
```json
{
  "mcpServers": {
    "thebrain": {
      "command": "C:\\Users\\YOUR_USER\\.local\\bin\\uv.exe",
      "args": ["run", "python", "C:\\Git\\thebrain-mcp\\python\\main.py"],
      "env": {
        "THEBRAIN_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Troubleshooting

### UV Not Found
```bash
# Add UV to PATH
export PATH="$HOME/.local/bin:$PATH"  # Unix
# or
$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"  # Windows
```

### Virtual Environment Issues
```bash
# Remove and recreate
rm -rf .venv
uv venv
uv pip install -e .
```

### Dependency Conflicts
```bash
# Force reinstall
uv pip install --force-reinstall -e .
```

### Cache Issues
```bash
# Clear UV cache
uv cache clean
```

## Best Practices

1. **Always use UV** for dependency management
2. **Keep pyproject.toml** as single source of truth
3. **Don't mix** pip and UV commands
4. **Use uv run** for consistent execution
5. **Commit uv.lock** for reproducible builds

## Migration from pip/requirements.txt

If you have an existing requirements.txt:
```bash
# Install from requirements.txt (one-time)
uv pip install -r requirements.txt

# Then update pyproject.toml and use UV going forward
uv pip install -e .
```

## Performance Comparison

| Operation | pip | UV |
|-----------|-----|-----|
| Install numpy | 5.2s | 0.4s |
| Install pandas | 8.7s | 0.6s |
| Install all deps | 45s | 3.2s |
| Resolve conflicts | 2m+ | 8s |

## Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [UV vs pip Comparison](https://astral.sh/blog/uv)
- [pyproject.toml Specification](https://packaging.python.org/en/latest/specifications/declaring-project-metadata/)

---

**Remember**: UV is not just faster—it's more reliable and provides consistent dependency resolution across all environments. Always use UV for this project! 🚀
