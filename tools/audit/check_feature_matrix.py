REQUIRED_ENDPOINTS = [
  "/import", "/import/preview",
  "/tree/export-json", "/tree/export", "/tree/export.xlsx",
  "/tree/stats", "/tree/progress", "/tree/parents/query",
  "/admin/clear", "/admin/clear-nodes",
  "/tree/conflicts/conflicts", "/tree/parent/{parent_id:int}/children",
  "/tree/next-incomplete-parent-json", "/tree/{parent_id:int}/slot/{slot:int}",
  "/tree/root-options", "/tree/navigate",
  "/dictionary", "/dictionary/export", "/dictionary/export.xlsx",
  "/tree/vm",
]

def feature_gaps(dual_map, routes_list):
    all_paths = set(r["path"] for r in routes_list)
    missing = []
    for p in REQUIRED_ENDPOINTS:
        # accept either typed or untyped params
        candidates = [p, p.replace("{parent_id:int}","{parent_id}").replace("{slot:int}","{slot}")]
        if not any(c in all_paths for c in candidates) and not any("/api/v1"+c in all_paths for c in candidates):
            missing.append(p)
    dual_missing = [bp for bp,st in dual_map.items() if bp != "/" and not (st["bare"] and st["v1"])]
    return {"missing_endpoints": missing, "dual_mount_missing": dual_missing}
