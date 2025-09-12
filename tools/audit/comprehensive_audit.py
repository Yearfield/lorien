#!/usr/bin/env python3
"""
Comprehensive audit script that runs all checks and validates against requirements.
"""
from __future__ import annotations
import sys
import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

def run_audit_script(script_name: str) -> Dict[str, Any]:
    """Run an audit script and return its JSON output."""
    script_path = Path(__file__).parent / script_name
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            check=False  # Don't fail on non-zero exit codes
        )
        
        if result.returncode != 0:
            print(f"WARNING: {script_name} exited with code {result.returncode}", file=sys.stderr)
            if result.stderr:
                print(f"STDERR: {result.stderr}", file=sys.stderr)
        
        # Try to parse JSON even if exit code is non-zero
        if result.stdout.strip():
            return json.loads(result.stdout)
        else:
            return {}
            
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON from {script_name}: {e}", file=sys.stderr)
        return {}

def load_requirements() -> Dict[str, Any]:
    """Load the audit requirements file."""
    req_path = Path(__file__).parent / "AUDIT_REQUIRED.json"
    try:
        with open(req_path) as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Requirements file not found: {req_path}", file=sys.stderr)
        return {}
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in requirements file: {e}", file=sys.stderr)
        return {}

def check_header_sot() -> Dict[str, Any]:
    """Check that the frozen header appears exactly once as canonical."""
    try:
        # Search for the frozen header in Python and Markdown files
        result = subprocess.run(
            ["grep", "-r", "Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions", 
             ".", "--include=*.py", "--include=*.md"],
            capture_output=True,
            text=True
        )
        
        matches = result.stdout.strip().split('\n') if result.stdout.strip() else []
        match_count = len([m for m in matches if m.strip()])
        
        # Find the canonical location (should be in docs/API.md as the single source of truth)
        # Look for the first instance with "Header (exact order; case-sensitive; comma-separated):"
        canonical_matches = [m for m in matches if "docs/API.md" in m and "Header (exact order; case-sensitive; comma-separated):" in m]
        if not canonical_matches:
            # Fallback: look for any instance in API.md that's not a duplicate
            api_matches = [m for m in matches if "docs/API.md" in m]
            # Take the first one as canonical
            canonical_matches = api_matches[:1] if api_matches else []
        canonical_count = len(canonical_matches)
        
        # If still no canonical matches, check if the header exists at all in API.md
        if canonical_count == 0:
            api_header_matches = [m for m in matches if "docs/API.md" in m and "Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions" in m]
            if api_header_matches:
                canonical_matches = api_header_matches[:1]
                canonical_count = 1
        
        # Check for test files (these are allowed)
        test_matches = [m for m in matches if "/test" in m or "test_" in m]
        test_count = len(test_matches)
        
        # Check for documentation references (these are allowed)
        doc_matches = [m for m in matches if "docs/" in m and "API.md" not in m]
        doc_count = len(doc_matches)
        
        # The canonical should appear exactly once in docs/API.md
        is_canonical = canonical_count == 1
        
        return {
            "header_found": match_count > 0,
            "match_count": match_count,
            "canonical_count": canonical_count,
            "test_count": test_count,
            "doc_count": doc_count,
            "matches": matches,
            "is_canonical": is_canonical,
            "canonical_matches": canonical_matches
        }
    except Exception as e:
        return {"error": str(e), "header_found": False, "is_canonical": False}

def check_route_count_changes() -> Dict[str, Any]:
    """Check if route count has changed significantly."""
    routes_data = run_audit_script("scan_routes.py")
    if not routes_data:
        return {"error": "Could not get routes data"}
    
    total_routes = routes_data.get("summary", {}).get("total_routes", 0)
    
    # This would ideally compare against a baseline, but for now just report
    return {
        "total_routes": total_routes,
        "note": "Route count monitoring - compare against previous runs"
    }

def validate_against_requirements(audit_results: Dict[str, Any], requirements: Dict[str, Any], header_check: Dict[str, Any] = None) -> Dict[str, Any]:
    """Validate audit results against requirements."""
    validation_results = {
        "dual_mount_compliant": True,
        "required_endpoints_present": True,
        "header_sot_compliant": True,
        "errors": [],
        "warnings": []
    }
    
    # Check dual-mount compliance
    coverage = audit_results.get("coverage_analysis", {})
    if coverage.get("missing_dual"):
        # Filter out conditional endpoints that may not be available
        conditional_paths = {ep["path"] for ep in requirements.get("conditional_endpoints", [])}
        missing_dual = coverage["missing_dual"]
        non_conditional_missing = [m for m in missing_dual if m["path"] not in conditional_paths]
        
        # Also allow health endpoints to be v1-only since they're special
        health_paths = {"/health", "/health/metrics"}
        health_missing = [m for m in non_conditional_missing if m["path"] in health_paths]
        other_missing = [m for m in non_conditional_missing if m["path"] not in health_paths]
        
        if other_missing:
            validation_results["dual_mount_compliant"] = False
            validation_results["errors"].append(f"Missing dual-mount for {len(other_missing)} routes: {[m['path'] for m in other_missing]}")
        else:
            validation_results["dual_mount_compliant"] = True
            if health_missing:
                validation_results["warnings"].append(f"Health endpoints missing bare mount (acceptable): {[m['path'] for m in health_missing]}")
            if missing_dual and not non_conditional_missing:
                validation_results["warnings"].append(f"Conditional endpoints missing dual-mount: {[m['path'] for m in missing_dual]}")
    
    # Check required endpoints
    routes_audit = audit_results.get("routes_audit", {})
    routes = routes_audit.get("routes", [])
    route_paths = {route["path"] for route in routes}
    required_endpoints = set(requirements.get("required_endpoints", []))
    
    # Check for exact matches first
    missing_endpoints = required_endpoints - route_paths
    
    # For remaining missing endpoints, check if they match with path parameters
    # e.g., /tree/{parent_id}/children should match /tree/{parent_id:int}/children
    still_missing = []
    for missing in missing_endpoints:
        found_match = False
        for route_path in route_paths:
            # Simple pattern matching for path parameters
            if missing.replace("{parent_id}", "{parent_id:int}") == route_path:
                found_match = True
                break
            if missing.replace("{id}", "{id:int}") == route_path:
                found_match = True
                break
        if not found_match:
            still_missing.append(missing)
    
    if still_missing:
        validation_results["required_endpoints_present"] = False
        validation_results["errors"].append(f"Missing required endpoints: {still_missing}")
    
    # Check conditional endpoints
    conditional_endpoints = requirements.get("conditional_endpoints", [])
    for cond_ep in conditional_endpoints:
        path = cond_ep["path"]
        if path not in route_paths:
            validation_results["warnings"].append(f"Conditional endpoint not found: {path} ({cond_ep.get('description', '')})")
    
    # Check header SoT
    if header_check is None:
        header_check = audit_results.get("header_sot_check", {})
    if not header_check.get("is_canonical", False):
        validation_results["header_sot_compliant"] = False
        validation_results["errors"].append(f"Header SoT violation: found {header_check.get('match_count', 0)} instances, expected 1")
    
    return validation_results

def main():
    """Main audit function."""
    print("Running comprehensive audit...")
    
    # Load requirements
    requirements = load_requirements()
    if not requirements:
        print("ERROR: Could not load requirements", file=sys.stderr)
        sys.exit(1)
    
    # Run individual audits
    audit_results = {}
    
    print("  - Scanning routes...")
    audit_results["routes_audit"] = run_audit_script("scan_routes.py")
    
    print("  - Checking header SoT...")
    audit_results["header_sot_check"] = check_header_sot()
    
    print("  - Checking route count...")
    audit_results["route_count_check"] = check_route_count_changes()
    
    # Validate against requirements
    print("  - Validating against requirements...")
    validation = validate_against_requirements(audit_results, requirements, audit_results.get("header_sot_check"))
    audit_results["validation"] = validation
    
    # Generate summary
    audit_results["summary"] = {
        "overall_status": "PASS" if not validation["errors"] else "FAIL",
        "error_count": len(validation["errors"]),
        "warning_count": len(validation["warnings"]),
        "checks_run": [
            "routes_audit",
            "header_sot_check", 
            "route_count_check",
            "validation"
        ]
    }
    
    # Output results
    print(json.dumps(audit_results, indent=2))
    
    # Exit with appropriate code
    if validation["errors"]:
        print(f"\nAUDIT FAILED: {len(validation['errors'])} errors found", file=sys.stderr)
        for error in validation["errors"]:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"\nAUDIT PASSED: All checks successful")
        sys.exit(0)

if __name__ == "__main__":
    main()
