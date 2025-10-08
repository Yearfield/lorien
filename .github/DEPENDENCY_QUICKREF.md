# Dependency Management Quick Reference

## 🔒 Lockfile System

We use **pip-tools** for deterministic dependency management with SHA256 hashes.

## 📦 Install Dependencies

```bash
# Development (most common)
pip install --require-hashes -r requirements-dev.txt

# Production only
pip install --require-hashes -r requirements.txt

# With editable install
pip install --require-hashes -r requirements-dev.txt
pip install -e . --no-deps
```

## 🔄 Update Lockfiles

```bash
# Using Makefile (recommended)
make -f Makefile.deps lock-deps

# Or manually
pip-compile requirements.in --generate-hashes
pip-compile requirements-dev.in --generate-hashes
```

## ➕ Add New Dependency

```bash
# 1. Add to source file
echo "package-name>=1.0.0" >> requirements.in

# 2. Regenerate lockfiles
make -f Makefile.deps lock-deps

# 3. Install
pip install --require-hashes -r requirements-dev.txt

# 4. Commit both files
git add requirements.in requirements.txt
git commit -m "Add package-name dependency"
```

## ⬆️ Upgrade Dependencies

```bash
# Upgrade all
make -f Makefile.deps upgrade-deps

# Upgrade specific package
make -f Makefile.deps upgrade-pkg PKG=fastapi

# Check for outdated
make -f Makefile.deps check-deps
```

## 🛡️ Security Audit

```bash
# Run security scan
make -f Makefile.deps check-security

# Or directly
pip-audit --require-hashes --requirement requirements.txt --strict
```

## ✅ Verify Lockfiles

```bash
# Check if lockfiles are in sync
./scripts/verify_lockfiles.sh

# Or using Makefile
make -f Makefile.deps verify-lockfiles
```

## 📊 Current Versions

**Known-Good Combination**:

- FastAPI: `0.115.0`
- Uvicorn: `0.30.6[standard]`
- Pydantic: `2.9.2`

```bash
# Show current versions
make -f Makefile.deps fastapi-info
```

## 🚫 Common Mistakes

### ❌ DON'T

```bash
# Don't edit lockfiles manually
vim requirements.txt  # ❌

# Don't use pip freeze
pip freeze > requirements.txt  # ❌

# Don't install without hashes in production
pip install -r requirements.txt  # ❌
```

### ✅ DO

```bash
# Edit source files
echo "new-package>=1.0" >> requirements.in  # ✅

# Use pip-compile
pip-compile requirements.in --generate-hashes  # ✅

# Use hash verification
pip install --require-hashes -r requirements.txt  # ✅
```

## 🔗 More Help

```bash
# Show all Makefile commands
make -f Makefile.deps help
```

**Full Documentation**: [docs/Dependencies.md](../docs/Dependencies.md)
