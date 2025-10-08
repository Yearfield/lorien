#!/bin/bash
# Lockfile Verification Script
# Ensures requirements.txt is in sync with requirements.in

set -e

echo "🔍 Verifying Lockfile Synchronization"
echo "======================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
ALL_CHECKS_PASSED=true

# Check if pip-compile is available
if ! command -v pip-compile &> /dev/null; then
    echo -e "${RED}✗${NC} pip-compile not found"
    echo "Install with: pip install pip-tools"
    exit 1
fi

# Check production requirements
echo "1️⃣  Checking production requirements..."
if [ ! -f "requirements.in" ]; then
    echo -e "${RED}✗${NC} requirements.in not found"
    ALL_CHECKS_PASSED=false
elif [ ! -f "requirements.txt" ]; then
    echo -e "${RED}✗${NC} requirements.txt not found - needs compilation"
    echo "   Run: pip-compile requirements.in --generate-hashes"
    ALL_CHECKS_PASSED=false
else
    # Compile to temp file and compare
    echo "   Compiling requirements.in (dry-run)..."
    if pip-compile requirements.in --dry-run --quiet --output-file=/tmp/requirements-check.txt 2>&1; then
        if diff -q requirements.txt /tmp/requirements-check.txt > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} requirements.txt is in sync"
        else
            echo -e "${RED}✗${NC} requirements.txt is OUT OF SYNC"
            echo ""
            echo "Differences found:"
            diff -u requirements.txt /tmp/requirements-check.txt | head -30
            echo ""
            echo "To fix: pip-compile requirements.in --generate-hashes"
            ALL_CHECKS_PASSED=false
        fi
    else
        echo -e "${RED}✗${NC} Failed to compile requirements.in"
        ALL_CHECKS_PASSED=false
    fi
fi
echo ""

# Check development requirements
echo "2️⃣  Checking development requirements..."
if [ ! -f "requirements-dev.in" ]; then
    echo -e "${RED}✗${NC} requirements-dev.in not found"
    ALL_CHECKS_PASSED=false
elif [ ! -f "requirements-dev.txt" ]; then
    echo -e "${RED}✗${NC} requirements-dev.txt not found - needs compilation"
    echo "   Run: pip-compile requirements-dev.in --generate-hashes"
    ALL_CHECKS_PASSED=false
else
    echo "   Compiling requirements-dev.in (dry-run)..."
    if pip-compile requirements-dev.in --dry-run --quiet --output-file=/tmp/requirements-dev-check.txt 2>&1; then
        if diff -q requirements-dev.txt /tmp/requirements-dev-check.txt > /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} requirements-dev.txt is in sync"
        else
            echo -e "${RED}✗${NC} requirements-dev.txt is OUT OF SYNC"
            echo ""
            echo "Differences found:"
            diff -u requirements-dev.txt /tmp/requirements-dev-check.txt | head -30
            echo ""
            echo "To fix: pip-compile requirements-dev.in --generate-hashes"
            ALL_CHECKS_PASSED=false
        fi
    else
        echo -e "${RED}✗${NC} Failed to compile requirements-dev.in"
        ALL_CHECKS_PASSED=false
    fi
fi
echo ""

# Check for security vulnerabilities
echo "3️⃣  Checking for security vulnerabilities..."
if command -v pip-audit &> /dev/null; then
    if pip-audit --require-hashes --requirement requirements.txt --desc 2>&1; then
        echo -e "${GREEN}✓${NC} No known vulnerabilities found"
    else
        echo -e "${RED}✗${NC} Security vulnerabilities detected!"
        echo "   Review output above and update affected packages"
        ALL_CHECKS_PASSED=false
    fi
else
    echo -e "${YELLOW}⊘${NC} pip-audit not installed (skipping security check)"
    echo "   Install with: pip install pip-audit"
fi
echo ""

# Check FastAPI/Uvicorn versions
echo "4️⃣  Checking FastAPI/Uvicorn versions..."
if [ -f "requirements.txt" ]; then
    FASTAPI_VERSION=$(grep "^fastapi==" requirements.txt | head -1 | cut -d'=' -f3 | cut -d' ' -f1)
    UVICORN_VERSION=$(grep "^uvicorn" requirements.txt | grep -v "    --hash" | head -1 | cut -d'=' -f3 | cut -d' ' -f1 | tr -d '[]')

    if [ -n "$FASTAPI_VERSION" ]; then
        echo -e "${GREEN}✓${NC} FastAPI $FASTAPI_VERSION"
    else
        echo -e "${YELLOW}⊘${NC} FastAPI version not found"
    fi

    if [ -n "$UVICORN_VERSION" ]; then
        echo -e "${GREEN}✓${NC} Uvicorn $UVICORN_VERSION"
    else
        echo -e "${YELLOW}⊘${NC} Uvicorn version not found"
    fi

    # Check for known-good combination
    if [ "$FASTAPI_VERSION" = "0.115.0" ] && [ "$UVICORN_VERSION" = "0.30.6[standard]" ]; then
        echo -e "${GREEN}✓${NC} Using known-good FastAPI/Uvicorn combination"
    elif [ -n "$FASTAPI_VERSION" ] && [ -n "$UVICORN_VERSION" ]; then
        echo -e "${YELLOW}ℹ${NC} Using FastAPI $FASTAPI_VERSION + Uvicorn $UVICORN_VERSION"
        echo "   Known-good: FastAPI 0.115.0 + Uvicorn 0.30.6"
    fi
fi
echo ""

# Check hash integrity
echo "5️⃣  Checking hash integrity..."
if [ -f "requirements.txt" ]; then
    HASH_COUNT=$(grep -c "    --hash=sha256:" requirements.txt || echo "0")
    if [ "$HASH_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓${NC} Found $HASH_COUNT SHA256 hashes"
    else
        echo -e "${RED}✗${NC} No hashes found in requirements.txt"
        echo "   Regenerate with: pip-compile requirements.in --generate-hashes"
        ALL_CHECKS_PASSED=false
    fi
else
    echo -e "${YELLOW}⊘${NC} requirements.txt not found"
fi
echo ""

# Final summary
echo "======================================"
if [ "$ALL_CHECKS_PASSED" = true ]; then
    echo -e "${GREEN}✅ All lockfile checks passed!${NC}"
    echo ""
    echo "Lockfiles are in sync and secure."
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some lockfile checks failed${NC}"
    echo ""
    echo "Fix lockfiles with:"
    echo "  make -f Makefile.deps lock-deps"
    echo ""
    echo "Or manually:"
    echo "  pip-compile requirements.in --generate-hashes"
    echo "  pip-compile requirements-dev.in --generate-hashes"
    echo ""
    exit 1
fi
