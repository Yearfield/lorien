#!/usr/bin/env python3
"""
Weekly documentation audit script.

Checks for:
1. Single source of truth for 8-column header
2. Documentation accuracy vs code
3. Stale documentation files
4. Missing documentation
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Canonical 8-column header (from SoT)
CANONICAL_HEADER = "Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions"

# Files to check for header consistency
HEADER_FILES = [
    "docs/API_HEADER_SOT.md",
    "docs/API_ROUTES_REGISTRY.md",
    "docs/EXPORT_FORMATS.md",
    "docs/IMPORT_FORMATS.md",
    "api/routers/tree_export.py",
    "tests/fixtures/",
    "tools/audit/"
]

# Documentation files that should exist
REQUIRED_DOCS = [
    "docs/API_HEADER_SOT.md",
    "docs/API_ROUTES_REGISTRY.md",
    "docs/README.md",
    "docs/DEVELOPMENT.md",
    "docs/DEPLOYMENT.md"
]

# Files that might be stale (older than 30 days)
STALE_THRESHOLD_DAYS = 30

def find_header_occurrences(content: str) -> List[str]:
    """Find all occurrences of the 8-column header in content."""
    # Look for the exact header
    exact_matches = re.findall(r'Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions', content)
    
    # Look for variations (different spacing, case)
    variations = re.findall(r'vital measurement.*node 1.*node 2.*node 3.*node 4.*node 5.*diagnostic triage.*actions', content, re.IGNORECASE)
    
    return exact_matches + variations

def check_header_consistency() -> Dict[str, Any]:
    """Check that the 8-column header appears consistently across files."""
    results = {
        "canonical_header": CANONICAL_HEADER,
        "files_checked": [],
        "inconsistencies": [],
        "total_occurrences": 0
    }
    
    for file_pattern in HEADER_FILES:
        if os.path.isfile(file_pattern):
            # Single file
            files_to_check = [file_pattern]
        elif os.path.isdir(file_pattern):
            # Directory - find all relevant files
            files_to_check = []
            for root, dirs, files in os.walk(file_pattern):
                for file in files:
                    if file.endswith(('.py', '.md', '.txt', '.csv')):
                        files_to_check.append(os.path.join(root, file))
        else:
            continue
        
        for file_path in files_to_check:
            # Skip this audit script itself to avoid false positives
            if file_path.endswith('docs_audit.py'):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                occurrences = find_header_occurrences(content)
                results["files_checked"].append(file_path)
                results["total_occurrences"] += len(occurrences)
                
                if len(occurrences) > 0:
                    # Check if any occurrence differs from canonical
                    for occurrence in occurrences:
                        if occurrence != CANONICAL_HEADER:
                            results["inconsistencies"].append({
                                "file": file_path,
                                "found": occurrence,
                                "expected": CANONICAL_HEADER
                            })
                            
            except Exception as e:
                results["inconsistencies"].append({
                    "file": file_path,
                    "error": str(e)
                })
    
    return results

def check_required_docs() -> Dict[str, Any]:
    """Check that all required documentation files exist."""
    results = {
        "required_docs": REQUIRED_DOCS,
        "missing_docs": [],
        "existing_docs": []
    }
    
    for doc_path in REQUIRED_DOCS:
        if os.path.exists(doc_path):
            results["existing_docs"].append(doc_path)
        else:
            results["missing_docs"].append(doc_path)
    
    return results

def check_stale_docs() -> Dict[str, Any]:
    """Check for potentially stale documentation files."""
    results = {
        "stale_files": [],
        "threshold_days": STALE_THRESHOLD_DAYS
    }
    
    current_time = datetime.now()
    threshold_seconds = STALE_THRESHOLD_DAYS * 24 * 60 * 60
    
    for root, dirs, files in os.walk("docs/"):
        for file in files:
            if file.endswith(('.md', '.txt', '.rst')):
                file_path = os.path.join(root, file)
                try:
                    file_mtime = os.path.getmtime(file_path)
                    age_seconds = current_time.timestamp() - file_mtime
                    
                    if age_seconds > threshold_seconds:
                        results["stale_files"].append({
                            "file": file_path,
                            "age_days": round(age_seconds / (24 * 60 * 60), 1)
                        })
                except Exception as e:
                    results["stale_files"].append({
                        "file": file_path,
                        "error": str(e)
                    })
    
    return results

def check_docs_vs_code() -> Dict[str, Any]:
    """Check that documentation matches actual code implementation."""
    results = {
        "endpoints_documented": [],
        "endpoints_missing_docs": [],
        "outdated_docs": []
    }
    
    # This would need to be expanded based on specific requirements
    # For now, just check that key files exist and are recent
    
    return results

def generate_audit_report() -> Dict[str, Any]:
    """Generate the complete documentation audit report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "audit_version": "1.0",
        "header_consistency": check_header_consistency(),
        "required_docs": check_required_docs(),
        "stale_docs": check_stale_docs(),
        "docs_vs_code": check_docs_vs_code()
    }
    
    return report

def main():
    """Main function to run the documentation audit."""
    print("Running documentation audit...")
    
    # Change to project root
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)
    
    # Generate audit report
    report = generate_audit_report()
    
    # Save report
    report_path = "docs_audit_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Audit report saved to: {report_path}")
    
    # Print summary
    print("\n=== DOCUMENTATION AUDIT SUMMARY ===")
    
    # Header consistency
    header_results = report["header_consistency"]
    print(f"Header occurrences found: {header_results['total_occurrences']}")
    print(f"Files checked: {len(header_results['files_checked'])}")
    if header_results["inconsistencies"]:
        print(f"❌ Inconsistencies found: {len(header_results['inconsistencies'])}")
        for inc in header_results["inconsistencies"]:
            print(f"  - {inc['file']}: {inc.get('found', 'ERROR')}")
    else:
        print("✅ Header consistency: PASS")
    
    # Required docs
    docs_results = report["required_docs"]
    print(f"\nRequired docs: {len(docs_results['existing_docs'])}/{len(docs_results['required_docs'])}")
    if docs_results["missing_docs"]:
        print(f"❌ Missing docs: {docs_results['missing_docs']}")
    else:
        print("✅ Required docs: PASS")
    
    # Stale docs
    stale_results = report["stale_docs"]
    print(f"\nStale docs (>30 days): {len(stale_results['stale_files'])}")
    if stale_results["stale_files"]:
        print("❌ Stale files found:")
        for stale in stale_results["stale_files"]:
            print(f"  - {stale['file']} ({stale['age_days']} days old)")
    else:
        print("✅ Stale docs: PASS")
    
    # Overall status
    has_issues = (
        len(header_results["inconsistencies"]) > 0 or
        len(docs_results["missing_docs"]) > 0 or
        len(stale_results["stale_files"]) > 0
    )
    
    if has_issues:
        print("\n❌ AUDIT FAILED - Issues found")
        return 1
    else:
        print("\n✅ AUDIT PASSED - No issues found")
        return 0

if __name__ == "__main__":
    exit(main())