import re, json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from tools.audit._util import list_dart_files, read_file

API_RE = re.compile(r'["\'](?:\$\{?\w+\.baseUrl\}?|[^"\']*?)(/api/v1/[^"\'\s]+|/[^"\'\s]+)["\']')
ROUTE_PUSH_RE = re.compile(r'pushNamed\s*\(\s*["\']([^"\']+)["\']')
TEXT_RE = re.compile(r'Text\s*\(\s*["\']([^"\']{3,})["\']')  # rough

# Keys we expect in UI (by literal text or Keys)
UI_EXPECT = {
  "workspace": [
    "Fix Incomplete Parents",
    "Fix Same parent BUT different children",
    "Open Calculator",
    "Open VM Builder",
    "Integrity Check",
    "Restore Backup",
    "View Stats",
    "Clear workspace (keep dictionary)",
    "Export CSV",
    "Export XLSX"
  ],
  "dictionary": [
    "Add Term",
    "Export CSV",
    "Export XLSX"
  ],
}

def scan():
    urls = set(); pushes = set(); texts = set(); files = list(list_dart_files())
    for p in files:
        s = read_file(p)
        for m in API_RE.finditer(s): urls.add(m.group(1))
        for m in ROUTE_PUSH_RE.finditer(s): pushes.add(m.group(1))
        for m in TEXT_RE.finditer(s): texts.add(m.group(1))
    return {"urls": sorted(urls), "pushes": sorted(pushes), "texts": sorted(texts)}

def ui_presence(scan_res):
    texts = set(scan_res["texts"])
    missing = {k: [t for t in v if t not in texts] for k,v in UI_EXPECT.items()}
    return {"missing": {k: v for k,v in missing.items() if v}, "ok": [t for t in texts if any(t in vv for vv in UI_EXPECT.values())]}
