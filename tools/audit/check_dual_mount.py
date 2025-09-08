from __future__ import annotations
import json
from typing import Dict, Any
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wiring_audit import collect_routes, map_dual_mount

def run_check() -> Dict[str, Any]:
    routes = collect_routes()
    pairs = map_dual_mount(routes)
    missing = {base: v for base, v in pairs.items() if not (v["bare"] and v["v1"])}
    return {"total_routes": len(routes), "missing_dual_mounts": missing, "ok": len(missing)==0}

if __name__ == "__main__":
    print(json.dumps(run_check(), indent=2))
