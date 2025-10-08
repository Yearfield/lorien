#!/bin/bash
# CI Setup Verification Script
# Run this to verify your local environment is ready for CI

set -e

echo "🔍 Verifying CI Setup for Lorien"
echo "================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
ALL_CHECKS_PASSED=true

# Function to check command availability
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "${RED}✗${NC} $1 is NOT installed"
        ALL_CHECKS_PASSED=false
        return 1
    fi
}

# Function to check Python package
check_python_package() {
    if python3 -c "import $1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Python package '$1' is installed"
        return 0
    else
        echo -e "${RED}✗${NC} Python package '$1' is NOT installed"
        ALL_CHECKS_PASSED=false
        return 1
    fi
}

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} File exists: $1"
        return 0
    else
        echo -e "${RED}✗${NC} File missing: $1"
        ALL_CHECKS_PASSED=false
        return 1
    fi
}

echo "1️⃣  Checking Core Tools"
echo "----------------------"
check_command python3
check_command pip
check_command git
echo ""

echo "2️⃣  Checking CI Dependencies"
echo "---------------------------"
check_python_package ruff
check_python_package mypy
check_python_package pytest
check_python_package mkdocs
echo ""

echo "3️⃣  Checking Optional Tools"
echo "-------------------------"
if check_command pre-commit; then
    echo -e "${YELLOW}ℹ${NC} Run 'pre-commit install' to enable hooks"
else
    echo -e "${YELLOW}ℹ${NC} Install with: pip install pre-commit"
fi

if check_python_package pip_audit; then
    :
else
    echo -e "${YELLOW}ℹ${NC} Install with: pip install pip-audit"
fi
echo ""

echo "4️⃣  Checking Configuration Files"
echo "-------------------------------"
check_file ".github/workflows/api-ci.yml"
check_file ".pre-commit-config.yaml"
check_file "pyproject.toml"
check_file "mkdocs.yml"
check_file "docs/CI.md"
echo ""

echo "5️⃣  Validating YAML Syntax"
echo "-------------------------"
for yaml_file in ".github/workflows/api-ci.yml" ".pre-commit-config.yaml" "mkdocs.yml"; do
    if python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Valid YAML: $yaml_file"
    else
        echo -e "${RED}✗${NC} Invalid YAML: $yaml_file"
        ALL_CHECKS_PASSED=false
    fi
done
echo ""

echo "6️⃣  Checking Python Version"
echo "-------------------------"
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 10 ]; then
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION (>= 3.10 required)"
else
    echo -e "${RED}✗${NC} Python $PYTHON_VERSION (>= 3.10 required)"
    ALL_CHECKS_PASSED=false
fi
echo ""

echo "7️⃣  Quick Lint Check (Sample)"
echo "----------------------------"
if command -v ruff &> /dev/null; then
    if ruff check --version &> /dev/null; then
        echo -e "${GREEN}✓${NC} Ruff is working correctly"
    else
        echo -e "${RED}✗${NC} Ruff installed but not working"
        ALL_CHECKS_PASSED=false
    fi
else
    echo -e "${YELLOW}⊘${NC} Skipped (ruff not installed)"
fi
echo ""

# Final summary
echo "================================="
if [ "$ALL_CHECKS_PASSED" = true ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    echo ""
    echo "Your environment is ready for CI development."
    echo ""
    echo "Next steps:"
    echo "  1. Install pre-commit: pip install pre-commit"
    echo "  2. Enable hooks: pre-commit install"
    echo "  3. Run all hooks: pre-commit run --all-files"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some checks failed${NC}"
    echo ""
    echo "Please install missing dependencies:"
    echo "  pip install -e .[dev]"
    echo ""
    exit 1
fi
