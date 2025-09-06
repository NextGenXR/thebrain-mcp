# TheBrain MCP Test Suite

## Structure

All test files are organized in this `tests/` directory for better project organization.

```
tests/
├── __init__.py              # Package marker
├── README.md               # This file
├── run_all_tests.py        # Master test runner
├── cleanup_tests.py        # Test organization utility
├── test_installation.py    # Installation verification
├── test_api.py            # API connectivity tests
├── test_graph_analysis.py  # Graph feature tests
├── test_hybrid_fix.py      # Hybrid mode tests
└── backups/               # Backup of removed test files
    ├── _backup_test_search_simple.py
    └── _backup_test_server.py
```

## Running Tests

### From Python Directory

```bash
# Run all tests
python tests/run_all_tests.py

# Run individual tests
python tests/test_installation.py
python tests/test_api.py
python tests/test_graph_analysis.py
python tests/test_hybrid_fix.py

# With UV
uv run python tests/run_all_tests.py
```

### From Tests Directory

```bash
cd tests

# Run all tests
python run_all_tests.py

# Run individual tests
python test_installation.py
python test_api.py
```

## Test Descriptions

### Core Tests (4 files)

| Test File | Purpose | Dependencies | When to Run |
|-----------|---------|--------------|-------------|
| `test_installation.py` | Verifies all components are installed correctly | None | After setup or environment changes |
| `test_api.py` | Tests API key validity and cloud connection | API key required | When experiencing connection issues |
| `test_graph_analysis.py` | Tests NetworkX graph analysis features | NetworkX, local Brain.db | After graph feature updates |
| `test_hybrid_fix.py` | Tests hybrid local/cloud functionality | API key + local DB | After performance changes |

### Test Utilities

- **`run_all_tests.py`** - Runs all tests in sequence with a summary report
- **`cleanup_tests.py`** - Organizes test files (already run)

## Environment Requirements

### Required
- Python 3.10+
- Dependencies installed (`uv pip install -e .`)

### Optional but Recommended
- Valid TheBrain API key in `.env` file
- Local Brain database at `~/Brains/U01/B02/Brain.db`
- NetworkX for graph analysis tests

## Test Coverage

The test suite covers:
- ✅ **Installation**: Package imports, environment setup
- ✅ **Connectivity**: API authentication, network access
- ✅ **Core Features**: Search, thought operations, navigation
- ✅ **Performance**: Hybrid mode, caching, optimization
- ✅ **Graph Analysis**: NetworkX integration, path finding
- ✅ **Dependencies**: All required and optional packages

## Quick Validation

For a quick validation that everything is working:

```bash
# From python directory
python tests/run_all_tests.py
```

This will run all tests and show a summary like:
```
✅ PASS | Installation        | All components installed
✅ PASS | API Connection      | Connection successful
✅ PASS | Graph Analysis      | Graph features available
✅ PASS | Hybrid Mode         | Hybrid modules loaded
----------------------------------------
Results: 4/4 tests passed
```

## Troubleshooting

### No API Key
- Create `.env` file with `THEBRAIN_API_KEY=your-key-here`
- Some tests will skip without an API key

### Import Errors
- Ensure you're in the `python` directory
- Run `uv pip install -e .` to install in development mode

### NetworkX Not Found
- Install with `uv pip install -e ".[visualization]"`
- Or just `pip install networkx pandas matplotlib`

### Local Database Not Found
- Tests will still pass but with limited functionality
- Local database improves performance but isn't required

## Adding New Tests

New test files should:
1. Be placed in this `tests/` directory
2. Follow naming convention `test_*.py`
3. Include clear docstrings
4. Be added to `run_all_tests.py` if part of core suite

## Maintenance

- Backup files in `backups/` can be deleted after confirming tests work
- Run `cleanup_tests.py` if test files get disorganized
- Keep test suite focused - each test should have unique purpose