#!/usr/bin/env bash
set -euo pipefail

# Lorien Beta Tagging Script
# This script creates the v6.8.0-beta.1 tag and prepares for release

ver="v6.8.0-beta.1"
echo "🚀 Preparing Lorien ${ver} for release..."

# Check if we're on main branch
current_branch=$(git branch --show-current)
if [[ "$current_branch" != "main" ]]; then
    echo "❌ Error: Must be on main branch to create release tag"
    echo "Current branch: $current_branch"
    exit 1
fi

# Check if working directory is clean
if [[ -n $(git status --porcelain) ]]; then
    echo "❌ Error: Working directory is not clean"
    echo "Please commit or stash all changes before creating release tag"
    git status --short
    exit 1
fi

# Check if tag already exists
if git tag -l | grep -q "^${ver}$"; then
    echo "❌ Error: Tag ${ver} already exists"
    exit 1
fi

# Verify all required files exist
required_files=(
    "core/version.py"
    "CHANGELOG.md"
    "docs/Release_Notes_${ver}.md"
    "docs/PreBeta_Execution_Tracker.md"
    "docs/Beta_SLA_Severity.md"
    "docs/Rollback_Plan.md"
    "docs/Beta_Acceptance_Checklist.md"
    "docs/Demo_Scripts.md"
    "scripts/audit_retention_sqlite.sql"
    "scripts/nightly_rotation.sh"
)

echo "🔍 Verifying required files..."
for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Error: Required file $file not found"
        exit 1
    fi
    echo "✅ $file"
done

# Verify version in core/version.py matches tag
version_in_file=$(grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+-beta\.[0-9]\+' core/version.py | head -1)
if [[ "$version_in_file" != "$ver" ]]; then
    echo "❌ Error: Version mismatch in core/version.py"
    echo "Expected: $ver"
    echo "Found: $version_in_file"
    exit 1
fi
echo "✅ Version in core/version.py matches tag"

# Run tests to ensure everything is working
echo "🧪 Running tests..."
if ! python -m pytest tests/test_csv_header_freeze.py -v; then
    echo "❌ Error: CSV header tests failed"
    exit 1
fi

# Check if API server can start (basic health check)
echo "🔌 Testing API health..."
if ! python -c "
import requests
import time
import subprocess
import sys

# Start API server in background
process = subprocess.Popen(['uvicorn', 'api.main:app', '--port', '8001'], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Wait for server to start
time.sleep(3)

try:
    response = requests.get('http://localhost:8001/health', timeout=5)
    if response.status_code == 200:
        print('✅ API health check passed')
        sys.exit(0)
    else:
        print(f'❌ API health check failed: {response.status_code}')
        sys.exit(1)
except Exception as e:
    print(f'❌ API health check error: {e}')
    sys.exit(1)
finally:
    process.terminate()
    process.wait()
"; then
    echo "❌ Error: API health check failed"
    exit 1
fi

# Create commit with all release files
echo "📝 Creating release commit..."
git add core/version.py CHANGELOG.md "docs/Release_Notes_${ver}.md"
git add docs/PreBeta_Execution_Tracker.md docs/Beta_SLA_Severity.md
git add docs/Rollback_Plan.md docs/Beta_Acceptance_Checklist.md
git add docs/Demo_Scripts.md scripts/audit_retention_sqlite.sql scripts/nightly_rotation.sh

git commit -m "chore(release): ${ver}

- Flutter parity: Calculator chained dropdowns, Workspace export
- Enhanced import/export UX with progress indicators
- Performance improvements: caching, backup/restore
- Comprehensive documentation and operational guides
- Beta acceptance checklist and rollback procedures"

# Create annotated tag
echo "🏷️ Creating annotated tag..."
git tag -a "${ver}" -m "Lorien ${ver}

Phase 6B Pre-Beta Release

Key Features:
- Flutter mobile parity
- Enhanced import/export experience  
- Performance optimization
- Backup/restore functionality
- Comprehensive operational documentation

Beta Window: Sep 2-9, 2025"

echo "✅ Tag ${ver} created successfully!"

# Show tag information
echo ""
echo "📋 Tag Information:"
git show --no-patch "${ver}"

echo ""
echo "🚀 Next Steps:"
echo "1. Push the commit: git push"
echo "2. Push the tag: git push --tags"
echo "3. Notify beta users"
echo "4. Begin beta testing period (Sep 2-9)"
echo "5. Monitor for issues and feedback"

echo ""
echo "🎯 Beta Acceptance Checklist:"
echo "Use docs/Beta_Acceptance_Checklist.md to validate deployment"

echo ""
echo "📚 Documentation:"
echo "- Release Notes: docs/Release_Notes_${ver}.md"
echo "- Demo Scripts: docs/Demo_Scripts.md"
echo "- Rollback Plan: docs/Rollback_Plan.md"
echo "- SLA Documentation: docs/Beta_SLA_Severity.md"

echo ""
echo "🎉 Lorien ${ver} is ready for beta testing!"
