# Code Quality & Formatting Guide

This guide covers code quality tools, formatting standards, and enforcement mechanisms for the Lorien project.

## Overview

Lorien enforces **strict code quality standards** with zero tolerance for warnings in CI. All code must pass:

- ✅ **Ruff** linting and formatting
- ✅ **Mypy** type checking (strict mode)
- ✅ **pip-audit** security scanning
- ✅ **Pytest** with warnings as errors
- ✅ **Pre-commit** hooks

## Quick Start

### 1. Install Pre-commit Hooks

**Required before first commit:**

```bash
pip install pre-commit
pre-commit install
```

### 2. Format Your Code

Before committing, ensure your code is properly formatted:

```bash
# Auto-fix most issues
ruff check . --fix
ruff format .

# Or run all pre-commit checks manually
pre-commit run --all-files
```

### 3. Verify CI Checks

Run the same checks that CI will run:

```bash
# Linting (fail on violations)
ruff check . --no-fix

# Formatting check
ruff format --check .

# Type checking
mypy api/ core/ storage/ --strict

# Security audit
pip-audit --strict --desc

# Tests with warnings as errors
pytest --strict-warnings --strict-markers
```

## Tools & Configuration

### Ruff

**Fast Python linter and formatter** that replaces Black, isort, flake8, and more.

**Configuration**: `pyproject.toml` → `[tool.ruff]` and `[tool.ruff.lint]`

**Key Settings**:

- Line length: 100 characters
- Target: Python 3.12
- Enabled rules: E, F, I, UP, B, SIM
- Auto-fixes available for most issues

**Usage**:

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check . --fix

# Format code
ruff format .

# Check formatting only
ruff format --check .
```

**Ignored Rules**:

- `E501`: Line too long (handled by formatter)
- `B008`: Function calls in argument defaults
- `B006`: Mutable data structures in argument defaults
- `B904`: Raise from exception handling (project-specific)
- `E402`: Module level import not at top (some modules need late imports)
- `F403`, `F405`: Star imports in `__init__.py` for public API

### Mypy

**Static type checker** ensuring type safety across the codebase.

**Configuration**: `pyproject.toml` → `[tool.mypy]`

**Strict Mode Settings**:

- `disallow_untyped_defs`: All functions must have type annotations
- `disallow_incomplete_defs`: Partial annotations not allowed
- `no_implicit_optional`: Explicit `| None` required
- `warn_return_any`: Warn when returning Any
- `warn_unused_ignores`: Fail on unnecessary type: ignore comments

**Usage**:

```bash
# Type check with strict mode
mypy api/ core/ storage/ --strict

# Check specific file
mypy api/routers/health.py --strict

# Show error codes
mypy api/ --strict --show-error-codes
```

**Common Patterns**:

```python
# Modern type hints (preferred)
from collections.abc import Iterable

def process_items(items: list[str]) -> dict[str, int]: ...
def get_user(user_id: int) -> User | None: ...
def handle_data(data: Iterable[str]) -> None: ...

# Avoid old-style typing
# ❌ from typing import List, Dict, Optional, Iterable
# ✅ Use built-in types and collections.abc
```

### pip-audit

**Security vulnerability scanner** for Python dependencies.

**Usage**:

```bash
# Audit all installed packages
pip-audit --strict --desc

# Audit requirements file with hashes
pip-audit --require-hashes --requirement requirements.txt --strict
```

**How it Works**:

- Checks all dependencies against PyPI Advisory Database
- Reports known CVEs with severity and description
- Fails on any known vulnerability
- Includes transitive dependencies

**Response to Vulnerabilities**:

1. Review the CVE details and severity
2. Update the vulnerable package if fix available
3. If no fix available, consider alternatives or mitigations
4. Document exceptions if temporary acceptance required

### Pre-commit Hooks

**Automated code quality checks** that run on every commit.

**Configuration**: `.pre-commit-config.yaml`

**Installed Hooks**:

1. **Ruff** (linting and formatting)
   - Auto-fixes issues when possible
   - Fails commit on unfixable violations

2. **Mypy** (type checking)
   - Runs on `api/`, `core/`, `storage/` only
   - Strict mode enabled
   - Includes stubs for pandas, pydantic, fastapi

3. **Standard Checks**:
   - Trailing whitespace removal
   - End-of-file fixing
   - Mixed line ending fixes
   - YAML/JSON/TOML validation
   - Large file detection (>1MB)
   - Merge conflict detection
   - Case conflict detection

4. **Security**:
   - detect-secrets: Prevents committing secrets/tokens
   - Private key detection

5. **Markdown**:
   - markdownlint with auto-fix

**Manual Invocation**:

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files
pre-commit run mypy --all-files

# Update hook versions
pre-commit autoupdate

# Skip hooks for emergency commits (discouraged)
git commit --no-verify
```

## Style Guidelines

### Python

**Line Length**: 100 characters (enforced by Ruff)

**Import Organization** (automatic via Ruff):

```python
# 1. Standard library imports
import os
import sys
from pathlib import Path

# 2. Third-party imports
import fastapi
import pandas as pd
from pydantic import BaseModel

# 3. Local application imports
from core.models import Node
from storage.sqlite import SQLiteRepository
```

**Type Hints** (required everywhere):

```python
# Functions must have full annotations
def process_data(
    items: list[str],
    config: dict[str, int] | None = None,
) -> tuple[int, str]:
    """Process items with optional config."""
    ...

# Async functions
async def fetch_data(node_id: int) -> Node | None:
    """Fetch node by ID."""
    ...

# Class methods
class TreeRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    async def get_node(self, node_id: int) -> Node | None:
        ...
```

**Docstrings** (Google style):

```python
def complex_function(param1: str, param2: int) -> dict[str, Any]:
    """Short description of function.

    Longer description if needed, explaining the function's purpose,
    behavior, and any important details.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Dictionary containing processed results

    Raises:
        ValueError: If param2 is negative
        HTTPException: If API call fails
    """
    ...
```

### Common Patterns

**Async/Await**:

```python
# All API endpoints must be async
@router.get("/nodes/{node_id}")
async def get_node(
    node_id: int,
    conn: sqlite3.Connection = Depends(get_db_connection),
) -> Node:
    # Wrap blocking SQLite calls with anyio.to_thread
    cur = await anyio.to_thread(conn.execute, "SELECT * FROM nodes WHERE id=?", (node_id,))
    row = await anyio.to_thread(cur.fetchone)

    # Use async repository methods
    repo = TreeRepository(conn)
    children = await repo.list_children(node_id)

    return Node(...)
```

**Error Handling**:

```python
# Prefer specific exceptions
try:
    data = process_data(items)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e)) from e

# Use context managers for resources
with closing(sqlite3.connect(db_path)) as conn:
    cur = conn.execute(query)
```

## CI Enforcement

All code must pass CI checks before merging. See `CI.md` for detailed pipeline documentation.

**Strict Mode**: All tools run with warnings as errors

- Ruff: `--no-fix --exit-non-zero-on-fix`
- Mypy: `--strict --warn-unused-ignores`
- Pytest: `--strict-warnings --strict-markers --strict-config`
- MkDocs: `--strict --verbose`
- pip-audit: `--strict --desc`

**Local Reproduction**:

```bash
# Run the exact CI checks locally
ruff check . --no-fix --exit-non-zero-on-fix
ruff format --check .
mypy api/ core/ storage/ --strict --warn-unused-ignores --warn-redundant-casts --warn-return-any
pip-audit --strict --desc
pytest --strict-warnings --strict-markers --strict-config
mkdocs build --strict --verbose
```

## FAQ

### Why strict mode?

**Prevents technical debt** - Warnings become errors tomorrow, catching them today is cheaper

**Maintains quality** - Consistent code style across the entire codebase

**Type safety** - Catches bugs at development time, not runtime

**Security** - Early detection of vulnerable dependencies

### Can I skip pre-commit hooks?

**Emergency only** with `git commit --no-verify`

**Not recommended** - CI will still fail if checks don't pass

**Better approach**: Fix issues rather than skip checks

### How do I fix Ruff violations?

Most issues auto-fix with:

```bash
ruff check . --fix
```

For manual fixes, Ruff provides helpful error messages with fix suggestions.

### What if Mypy complains about third-party libraries?

Add type stubs or configure overrides in `pyproject.toml`:

```toml
[[tool.mypy.overrides]]
module = ["third_party_lib.*"]
ignore_missing_imports = true
```

### How do I handle security vulnerabilities?

1. **Check severity**: Critical/High require immediate action
2. **Update package**: `pip install --upgrade vulnerable-package`
3. **Regenerate lockfile**: `pip-compile requirements.in --generate-hashes`
4. **Test thoroughly**: Ensure compatibility
5. **If no fix**: Document exception and mitigation plan

## References

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [pip-audit Documentation](https://pypi.org/project/pip-audit/)
- [pre-commit Documentation](https://pre-commit.com/)
- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)

---

**Last Updated**: October 8, 2025
**Maintained by**: Lorien Development Team
