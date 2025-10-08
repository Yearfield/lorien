# CI Quick Reference

## 🚀 Before You Push

Run these commands locally to catch CI failures early:

```bash
# 1. Lint (auto-fix)
ruff check . --fix
ruff format .

# 2. Type check
mypy api/ core/ storage/ --strict

# 3. Tests
pytest --strict-warnings --cov=api --cov=core --cov=storage

# 4. Security audit
pip-audit --strict --desc

# 5. Docs build
mkdocs build --strict
```

## 🔧 Install Pre-commit Hooks

Automatically run checks before each commit:

```bash
pip install pre-commit
pre-commit install
```

## 📊 CI Jobs Overview

| Job | Tool | Fails On |
|-----|------|----------|
| **Lint** | Ruff | Any style violation or formatting issue |
| **Type Check** | Mypy | Any type error or warning |
| **Security** | pip-audit | Known vulnerabilities in dependencies |
| **Docs** | MkDocs | Broken links, invalid markdown |
| **Test** | Pytest | Any test failure or warning |
| **Wiring Audit** | Custom | API/UI inconsistencies |

## ⚠️ Common Failures

### Ruff Lint Failure

```bash
# Fix automatically
ruff check . --fix
ruff format .
```

### Mypy Type Error

- Add type annotations to functions
- Check function return types
- Review `pyproject.toml` for overrides

### pip-audit Vulnerability

- Update affected package: `pip install --upgrade <package>`
- Check for security advisories
- Consider alternative packages if no fix available

### MkDocs Build Error

- Verify all nav links in `mkdocs.yml` exist
- Check for broken internal links
- Validate markdown syntax

### Test Failure

- Run locally: `pytest -v`
- Check test output in CI artifacts
- Verify database state if needed

## 🎯 Strict Mode

All tools run in **strict mode** — warnings are errors!

**Why?**

- Catch bugs early
- Maintain code quality
- Prevent technical debt
- Ensure security

## 📦 Python Versions Tested

CI runs tests on:

- Python 3.10
- Python 3.11
- Python 3.12

## 🔗 Useful Links

- [Full CI Documentation](../docs/CI.md)
- [Ruff Rules](https://docs.astral.sh/ruff/rules/)
- [Mypy Cheatsheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)
- [pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

## 🐛 Debugging CI

View detailed logs:

1. Go to Actions tab in GitHub
2. Click on failed workflow run
3. Click on failed job
4. Expand failed step

Download artifacts:

- Test results (JUnit XML)
- Coverage reports
- Documentation build
- Audit reports
