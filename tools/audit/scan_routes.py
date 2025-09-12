#!/usr/bin/env python3
"""
Scan backend routes and verify dual-mount coverage.
"""
from __future__ import annotations
from typing import List, Dict, Any, Set
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tools.audit._util import import_app
from fastapi.routing import APIRoute

ROUTE_EXCLUDES = (
    "/openapi.json", "/docs", "/redoc", "/docs/oauth2-redirect", "/health"
)

def collect_routes() -> List[Dict[str, Any]]:
    """Collect all API routes from the FastAPI app."""
    app = import_app()
    routes = []
    seen_paths = set()
    
    for route in app.routes:
        if isinstance(route, APIRoute):
            path = route.path
            if any(path.startswith(ex) for ex in ROUTE_EXCLUDES):
                continue
            
            # Convert /api/v1/path to /path for base path
            base_path = path
            if path.startswith("/api/v1/"):
                base_path = path[len("/api/v1"):]  # Keep leading /
            elif path.startswith("/api/v1"):
                base_path = "/"
            
            # Create a unique key for deduplication
            route_key = (base_path, tuple(sorted(route.methods or [])))
            if route_key not in seen_paths:
                seen_paths.add(route_key)
                routes.append({
                    "path": base_path,
                    "name": route.name,
                    "methods": sorted(list(route.methods or [])),
                })
    
    routes.sort(key=lambda x: (x["path"], ",".join(x["methods"])))
    return routes

def map_dual_mount(routes: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Map routes to dual-mount status (bare vs /api/v1)."""
    # Since routes are now collected as base paths, we need to check the original app routes
    # to determine dual-mount status
    app = import_app()
    dual_map = {}
    
    # Collect all original routes from the app
    for route in app.routes:
        if isinstance(route, APIRoute):
            path = route.path
            if any(path.startswith(ex) for ex in ROUTE_EXCLUDES):
                continue
            
            # Determine base path
            base_path = path
            if path.startswith("/api/v1/"):
                base_path = path[len("/api/v1"):]  # Keep leading /
            elif path.startswith("/api/v1"):
                base_path = "/"
            
            # Initialize if not exists
            if base_path not in dual_map:
                dual_map[base_path] = {"bare": False, "v1": False, "examples": []}
            
            # Mark as bare or v1 based on original path
            if path.startswith("/api/v1/"):
                dual_map[base_path]["v1"] = True
            else:
                dual_map[base_path]["bare"] = True
            
            dual_map[base_path]["examples"].append(path)
    
    return dual_map

def check_dual_mount_coverage(dual_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Check which routes have complete dual-mount coverage."""
    missing_dual = []
    complete_dual = []
    
    for base_path, info in dual_map.items():
        if info["bare"] and info["v1"]:
            complete_dual.append(base_path)
        else:
            missing_dual.append({
                "path": base_path,
                "has_bare": info["bare"],
                "has_v1": info["v1"],
                "examples": info["examples"]
            })
    
    return {
        "complete_dual": complete_dual,
        "missing_dual": missing_dual,
        "total_routes": len(dual_map),
        "coverage_percent": len(complete_dual) / len(dual_map) * 100 if dual_map else 0
    }

def main():
    """Main function to scan routes and output results."""
    try:
        routes = collect_routes()
        dual_map = map_dual_mount(routes)
        coverage = check_dual_mount_coverage(dual_map)
        
        result = {
            "routes": routes,
            "dual_mount_analysis": dual_map,
            "coverage_analysis": coverage,
            "summary": {
                "total_routes": len(routes),
                "dual_mount_complete": len(coverage["complete_dual"]),
                "dual_mount_missing": len(coverage["missing_dual"]),
                "coverage_percent": coverage["coverage_percent"]
            }
        }
        
        print(json.dumps(result, indent=2))
        
        # Exit with error code if dual-mount coverage is incomplete
        if coverage["missing_dual"]:
            print(f"\nERROR: {len(coverage['missing_dual'])} routes missing dual-mount coverage", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"\nSUCCESS: All {len(routes)} routes have dual-mount coverage")
            
    except Exception as e:
        print(f"ERROR: Failed to scan routes: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
