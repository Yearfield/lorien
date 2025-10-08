# CI/CD Pipeline

## Overview

Lorien uses GitHub Actions for comprehensive continuous integration. The CI pipeline enforces code quality, security, and correctness with **zero tolerance for warnings**.

## Pipeline Jobs

### 1. **Lint with Ruff** 🔍

- **Purpose**: Enforce code style and catch common errors
- **Tool**: Ruff (modern, fast Python linter)
- **Flags**: `--no-fix --exit-non-zero-on-fix`
- **Checks**:
  - Code style violations (pycodestyle)
  - Common bugs (flake8-bugbear)
  - Import sorting (isort)
  - Modern Python patterns (pyupgrade)
  - Code simplification opportunities
  - Formatting consistency
- **Failure**: Any linting violation or formatting issue fails the build

### 2. **Type Check with Mypy** 🔒

- **Purpose**: Ensure type safety across the codebase
- **Tool**: Mypy with strict mode
- **Configuration**: `pyproject.toml` with strict settings
- **Flags**: `--strict --warn-unused-ignores --warn-redundant-casts --warn-return-any`
- **Checks**:
  - All functions have type annotations
  - No implicit `Any` types
  - No untyped decorators
  - Redundant casts and unused ignores flagged
- **Failure**: Any type error or warning fails the build

### 3. **Security Audit with pip-audit** 🛡️

- **Purpose**: Detect known security vulnerabilities in dependencies
- **Tool**: pip-audit (official PyPA tool)
- **Flags**: `--strict --desc`
- **Checks**:
  - All installed packages against PyPI Advisory Database
  - Known CVEs and security issues
  - Transitive dependencies included
- **Failure**: Any known vulnerability fails the build
- **Note**: Run `pip-audit` locally before committing to catch issues early

### 4. **Documentation Build with MkDocs** 📚

- **Purpose**: Ensure documentation builds without errors
- **Tool**: MkDocs with Material theme
- **Flags**: `--strict --verbose`
- **Checks**:
  - All markdown files parse correctly
  - All internal links are valid
  - Navigation structure is complete
  - No broken references or missing pages
- **Output**: Generates static site in `site/` directory
- **Failure**: Any warning or error in documentation fails the build
- **Artifact**: Built site uploaded for preview

### 5. **Test with Pytest** ✅

- **Purpose**: Run comprehensive test suite
- **Tool**: Pytest with coverage reporting
- **Flags**: `--strict-warnings --strict-markers --strict-config`
- **Matrix**: Tests run on Python 3.10, 3.11, and 3.12
- **Checks**:
  - All unit tests pass
  - All integration tests pass
  - Code coverage is measured
  - Test warnings treated as errors
- **Coverage**: Reports generated for `api/`, `core/`, and `storage/`
- **Failure**: Any test failure or warning fails the build
- **Artifacts**: JUnit XML and coverage reports uploaded

### 6. **Wiring Audit** 🔌

- **Purpose**: Ensure API endpoint consistency between backend and frontend
- **Dependencies**: Runs after lint, type-check, and test pass
- **Checks**:
  - Dual-mount coverage (bare + `/api/v1` prefix)
  - Header Single Source of Truth (8-column frozen header)
  - API contract consistency
  - Route coverage across layers
- **Failure**: Any inconsistency in API wiring fails the build

### 7. **CI Success** ✨

- **Purpose**: Final gate ensuring all jobs passed
- **Dependencies**: All previous jobs
- **Behavior**: Fails if any upstream job failed
- **Output**: Clear success/failure message

## Local Development

### Running CI Checks Locally

Before pushing, run these commands to catch issues early:

```bash
# Lint check
ruff check . --no-fix
ruff format --check .

# Type check
mypy api/ core/ storage/ --strict

# Security audit
pip-audit --strict --desc

# Documentation build
mkdocs build --strict --verbose

# Tests
pytest --strict-warnings --strict-markers --strict-config \
  --cov=api --cov=core --cov=storage

# Wiring audit
python tools/audit/wiring_audit.py
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run checks:

```bash
pip install pre-commit
pre-commit install
```

## Configuration Files

- **Ruff**: `pyproject.toml` → `[tool.ruff]` and `[tool.ruff.lint]`
- **Mypy**: `pyproject.toml` → `[tool.mypy]`
- **Pytest**: `pyproject.toml` → `[tool.pytest.ini_options]`
- **Coverage**: `pyproject.toml` → `[tool.coverage.*]`
- **MkDocs**: `mkdocs.yml`
- **GitHub Actions**: `.github/workflows/api-ci.yml`

## Strict Mode Philosophy

All CI tools are configured in **strict mode** with **warnings as errors**:

- **Rationale**: Catch issues early, maintain high code quality
- **Benefits**:
  - Prevents technical debt accumulation
  - Ensures consistent code style
  - Catches bugs before production
  - Maintains type safety
  - Enforces security best practices
- **Trade-offs**: May require more upfront fixes, but saves time long-term

## Workflow Triggers

The CI pipeline runs on:

- **Push** to `main` or `develop` branches
- **Pull Requests** to `main` or `develop` branches
- **Path filters**: Only runs when relevant files change:
  - Python code: `api/`, `core/`, `storage/`, `tests/`
  - Config: `pyproject.toml`, `requirements.txt`
  - Docs: `docs/`, `mkdocs.yml`

## Caching Strategy

GitHub Actions caches pip dependencies to speed up CI:

- **Cache key**: OS + Python version + dependency file hashes
- **Restore keys**: Fallback to previous caches if exact match not found
- **Benefit**: Significantly faster CI runs after first build

## Troubleshooting

### CI Fails on Lint

```bash
# Auto-fix linting issues
ruff check . --fix
ruff format .
```

### CI Fails on Type Check

- Add missing type annotations
- Review Mypy output for specific issues
- Check `pyproject.toml` overrides if legitimate

### CI Fails on Security Audit

- Review CVE details from pip-audit output
- Update vulnerable packages
- If no fix available, consider alternatives or mitigations

### CI Fails on Documentation Build

- Check for broken links in markdown
- Verify all files in `mkdocs.yml` nav exist
- Run `mkdocs build --strict --verbose` locally for details

### CI Fails on Tests

- Run tests locally with same flags
- Check for environment-specific issues
- Review test output in uploaded JUnit XML artifacts

## Future Enhancements

- [ ] Add Flutter UI tests to CI (currently separate workflow)
- [ ] Code coverage thresholds with enforcement
- [ ] Performance regression tests
- [ ] Docker image builds
- [ ] Deployment automation
- [ ] Dependency update automation (Dependabot)
- [ ] Release note generation

## References

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Mypy Documentation](https://mypy.readthedocs.io/)
- [pip-audit Documentation](https://pypi.org/project/pip-audit/)
- [MkDocs Documentation](https://www.mkdocs.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

**Last Updated**: October 8, 2025
**Maintained by**: Lorien Development Team
