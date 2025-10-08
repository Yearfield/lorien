# Dependency Management

## Overview

Lorien uses **pip-tools** for deterministic dependency management with cryptographic hash verification. All dependencies are locked to specific versions with SHA256 hashes for security and reproducibility.

## 🔒 Lockfile Strategy

### Files

| File | Purpose | Compiled From |
|------|---------|---------------|
| `requirements.in` | Production dependencies (source) | Manual |
| `requirements.txt` | Locked production deps with hashes | `requirements.in` |
| `requirements-dev.in` | Development dependencies (source) | Manual |
| `requirements-dev.txt` | Locked dev deps with hashes | `requirements-dev.in` |

### Why Lockfiles?

✅ **Reproducibility**: Same dependencies across all environments
✅ **Security**: SHA256 hash verification prevents tampering
✅ **Stability**: Known-good version combinations
✅ **CI Speed**: Faster installs with pre-resolved dependencies
✅ **Vulnerability Tracking**: pip-audit works best with lockfiles

## 🚀 Quick Start

### Install Dependencies

```bash
# Production only
pip install --require-hashes -r requirements.txt

# Development (includes production)
pip install --require-hashes -r requirements-dev.txt

# With editable project install
pip install --require-hashes -r requirements-dev.txt
pip install -e . --no-deps
```

### Update Lockfiles

```bash
# Using Makefile (recommended)
make -f Makefile.deps lock-deps

# Using pip-compile directly
pip-compile requirements.in --generate-hashes --output-file=requirements.txt
pip-compile requirements-dev.in --generate-hashes --output-file=requirements-dev.txt
```

## 📦 Common Tasks

### Adding a New Dependency

1. **Add to source file**:

   ```bash
   # For production
   echo "new-package>=1.0.0" >> requirements.in

   # For development
   echo "new-dev-tool>=1.0.0" >> requirements-dev.in
   ```

2. **Recompile lockfiles**:

   ```bash
   make -f Makefile.deps lock-deps
   ```

3. **Install and test**:

   ```bash
   pip install --require-hashes -r requirements-dev.txt
   ```

4. **Commit all files**:

   ```bash
   git add requirements*.in requirements*.txt
   git commit -m "Add new-package dependency"
   ```

### Upgrading Dependencies

#### Upgrade All

```bash
# Using Makefile
make -f Makefile.deps upgrade-deps

# Using pip-compile
pip-compile requirements.in --upgrade --generate-hashes
pip-compile requirements-dev.in --upgrade --generate-hashes
```

#### Upgrade Specific Package

```bash
# Using Makefile
make -f Makefile.deps upgrade-pkg PKG=fastapi

# Using pip-compile
pip-compile requirements.in --upgrade-package fastapi --generate-hashes
```

### Checking for Updates

```bash
# See outdated packages
make -f Makefile.deps check-deps

# Or use pip directly
pip list --outdated
```

### Security Auditing

```bash
# Using Makefile
make -f Makefile.deps check-security

# Using pip-audit directly
pip-audit --require-hashes --requirement requirements.txt --strict --desc
```

## 🔧 Known-Good Combinations

### FastAPI + Uvicorn

**Current (2025-10-08)**:

- `fastapi==0.115.0` + `uvicorn[standard]==0.30.6` ✅
- `pydantic==2.9.2`

**Previously Tested**:

- `fastapi==0.114.0` + `uvicorn==0.30.5`
- `fastapi==0.111.0` + `uvicorn==0.29.0`

### Why These Versions?

- **FastAPI 0.115.0**: Latest stable with Pydantic v2 support
- **Uvicorn 0.30.6**: Performance improvements and WebSocket stability
- **Pydantic 2.9.2**: Type validation optimizations

**Pinning Philosophy**: We pin to specific patch versions to avoid surprises, but upgrade regularly (monthly).

## 🛡️ Hash Verification

All lockfiles include SHA256 hashes for tamper detection:

```txt
fastapi==0.115.0 \
    --hash=sha256:17ea427674467486e997206a461e20e4e4b20d... \
    --hash=sha256:c3a3f67d4f3b8d8e3f4c3a7b8d7e6f5e8d9a0b...
```

**Benefits**:

- Prevents supply chain attacks
- Detects compromised packages
- Ensures binary reproducibility
- Required for secure deployments

## 🤖 CI Integration

### Lockfile Verification

CI automatically verifies lockfiles are in sync:

```yaml
- name: Verify lockfiles are in sync
  run: |
    pip-compile requirements.in --dry-run --quiet -o /tmp/check.txt
    diff requirements.txt /tmp/check.txt || exit 1
```

### Installation in CI

```yaml
- name: Install dependencies from lockfile
  run: |
    pip install --require-hashes -r requirements.txt
    pip install --require-hashes -r requirements-dev.txt
    pip install -e . --no-deps
```

## 📋 Best Practices

### ✅ DO

- Always use `--require-hashes` in production
- Pin exact versions in `.in` files for critical deps
- Upgrade dependencies regularly (monthly)
- Run security audits before merging PRs
- Commit both `.in` and `.txt` files together
- Test upgrades in CI before merging

### ❌ DON'T

- Edit `.txt` files manually (always regenerate)
- Install without hash verification in production
- Use `pip freeze` instead of pip-compile
- Mix pip-tools with other lock strategies
- Skip lockfile verification in CI
- Deploy without security audit

## 🔍 Troubleshooting

### Lockfile Out of Sync

**Error**: `requirements.txt is out of sync with requirements.in`

**Solution**:

```bash
make -f Makefile.deps lock-deps
git add requirements*.txt
git commit -m "Update lockfiles"
```

### Hash Mismatch

**Error**: `THESE PACKAGES DO NOT MATCH THE HASHES FROM THE REQUIREMENTS FILE`

**Cause**: Package was modified or corrupted

**Solution**:

1. Clear pip cache: `pip cache purge`
2. Regenerate lockfiles: `make -f Makefile.deps lock-deps`
3. If persists, check for compromised package

### Dependency Conflict

**Error**: `Cannot install X and Y because these package versions have conflicting dependencies`

**Solution**:

1. Check `requirements.in` for version constraints that conflict
2. Loosen version pins if safe
3. Use `--resolver=backtracking` (default in our setup)

### pip-tools Not Found

**Error**: `command not found: pip-compile`

**Solution**:

```bash
# Install pip-tools
make -f Makefile.deps install-pip-tools

# Or directly
pip install pip-tools
```

## 📚 Makefile Commands

Full list of available commands:

```bash
make -f Makefile.deps help
```

Key commands:

- `lock-deps` - Compile lockfiles with hashes
- `sync-deps` - Install exact versions from lockfiles
- `upgrade-deps` - Upgrade all dependencies
- `check-security` - Run security audit
- `verify-lockfiles` - Check if lockfiles are in sync
- `fastapi-info` - Show FastAPI/Uvicorn versions

## 🔗 Alternative: uv

While we use pip-tools, **uv** is a faster alternative:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Compile with uv
uv pip compile requirements.in -o requirements.txt --generate-hashes

# Sync with uv (much faster!)
uv pip sync requirements.txt
```

**Note**: uv is compatible with pip-tools lockfiles. Switch at your discretion.

## 📖 References

- [pip-tools Documentation](https://pip-tools.readthedocs.io/)
- [pip-audit Documentation](https://github.com/pypa/pip-audit)
- [PEP 665: Specifying Installation Requirements](https://peps.python.org/pep-0665/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [Supply Chain Security Best Practices](https://www.cisa.gov/sbom)

---

**Last Updated**: October 8, 2025
**Maintained by**: Lorien Development Team
