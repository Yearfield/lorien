import json, os, datetime, textwrap, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tools.audit._util import ROOT, run
from tools.audit.scan_backend import collect_routes, dual_mount_map
from tools.audit.scan_flutter import scan as scan_flutter, ui_presence
from tools.audit.check_feature_matrix import feature_gaps

def main():
    routes = collect_routes()
    dual = dual_mount_map(routes)
    flutter = scan_flutter()
    ui = ui_presence(flutter)
    gaps = feature_gaps(dual, routes)

    # pytest summary (best effort)
    code, out, err = run(["pytest","-q"])
    pytest_summary = (out + "\n" + err).strip()

    # Build markdown
    md = []
    md.append(f"# Wiring Audit Report\n\nGenerated: `{datetime.datetime.utcnow().isoformat(timespec='seconds')}Z`")
    md.append("\n## Backend routes (sample)")
    md.append("| Path | Methods | Name |")
    md.append("| --- | --- | --- |")
    for r in sorted(routes, key=lambda x: x["path"])[:200]:
        md.append(f"| {r['path']} | {','.join(r['methods'])} | {r['name']} |")
    md.append("\n## Dual-mount compliance")
    md.append("| Base Path | Bare | v1 | Example(s) |")
    md.append("| --- | --- | --- | --- |")
    for bp, st in sorted(dual.items()):
        md.append(f"| {bp} | {st['bare']} | {st['v1']} | {', '.join(st['examples'][:2])} |")
    md.append("\n**Missing dual-mount for:**\n\n- " + "\n- ".join(gaps["dual_mount_missing"]) if gaps["dual_mount_missing"] else "\nAll routes dual-mounted ✅")

    md.append("\n## Required features coverage")
    if gaps["missing_endpoints"]:
        md.append("**Missing endpoints:**")
        for m in gaps["missing_endpoints"]:
            md.append(f"- {m}")
    else:
        md.append("All required endpoints present ✅")

    md.append("\n## Flutter scan")
    md.append("### API URLs discovered")
    md.append("\n".join(f"- `{u}`" for u in flutter["urls"]))
    md.append("\n### pushNamed routes")
    md.append("\n".join(f"- `{p}`" for p in flutter["pushes"]))
    md.append("\n### UI presence check")
    if ui["missing"]:
        md.append("**Missing UI texts:**")
        for group, items in ui["missing"].items():
            md.append(f"- {group}: " + ", ".join(items))
    else:
        md.append("All expected UI actions/texts found in Flutter sources ✅")

    md.append("\n## Pytest summary\n")
    md.append("```\n" + pytest_summary + "\n```")

    # Write file
    out_path = os.path.join(ROOT, "AUDIT_REPORT.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    main()
