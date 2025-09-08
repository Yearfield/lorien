from __future__ import annotations
import os, json, datetime
from typing import Dict, Any, List
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import REPO_ROOT, run
from wiring_audit import collect_routes, map_dual_mount
from scan_dart_api_calls import scan_dart
from check_dual_mount import run_check as dual_check

REPORT = os.path.join(REPO_ROOT, "AUDIT_REPORT.md")

def md_table(headers: List[str], rows: List[List[str]]) -> str:
    h = "| " + " | ".join(headers) + " |"
    d = "| " + " | ".join(["---"]*len(headers)) + " |"
    rs = ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join([h, d] + rs)

def main():
    print("Getting timestamp...")
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    print("Collecting routes...")
    routes = collect_routes()
    print(f"Found {len(routes)} routes")
    pairs  = map_dual_mount(routes)
    print("Scanning Dart files...")
    dart   = scan_dart()
    print("Checking dual mounts...")
    dual   = dual_check()

    # pytest quick run (summary only)
    code, out, err = run(["pytest","-q"], cwd=REPO_ROOT, timeout=300)
    pytest_summary = "\n".join([l for l in out.splitlines() if l.strip().endswith("passed") or "failed" in l])

    # Build sections
    route_rows = [[r["path"], ",".join(r["methods"]), r["name"]] for r in routes]
    dual_rows  = [[base, "OK" if v["bare"] and v["v1"] else "MISSING", ", ".join(v["examples"])] for base, v in sorted(pairs.items())]
    api_rows   = [[u] for u in dart["api_urls"]]

    md = []
    md.append(f"# Wiring Audit Report\n\nGenerated: `{ts}`\n")
    md.append("## Backend routes\n")
    md.append(md_table(["Path","Methods","Name"], route_rows) or "_No routes_")
    md.append("\n\n## Dual-mount compliance\n")
    md.append(md_table(["Base Path","Status","Examples"], dual_rows) or "_No data_")
    if not dual["ok"]:
        md.append("\n⚠️ **Missing dual mounts:**\n")
        for base, v in dual["missing_dual_mounts"].items():
            md.append(f"- `{base}` → present: bare={v['bare']}, v1={v['v1']} · {', '.join(v['examples'])}")
    md.append("\n\n## Flutter API URLs discovered\n")
    md.append(md_table(["URL / Path"], api_rows) or "_None found_")
    md.append("\n\n## Flutter pushNamed routes\n")
    md.append(md_table(["Route"], [[r] for r in dart["push_routes"]]) or "_None_")
    md.append("\n\n## Pytest summary\n")
    md.append("```\n" + (pytest_summary or out[-2000:]) + "\n```\n")

    open(REPORT,"w",encoding="utf-8").write("\n".join(md))
    print(f"Wrote {REPORT}")

if __name__ == "__main__":
    print("Starting audit report generation...")
    main()
    print("Audit report generation complete.")
