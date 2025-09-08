from __future__ import annotations
import os, re, json
from typing import List, Dict, Set, Tuple
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _util import UI_ROOT

HTTP_RE = re.compile(r"""Uri\.parse\(\s*['"](?P<url>[^'"]+)['"]\s*\)""")
RAW_PATH_RE = re.compile(r"""['"](/api/v1/[^'"]+|/[a-zA-Z0-9][^'"]+)['"]""")
ROUTE_PUSH_RE = re.compile(r"""pushNamed\(\s*['"](?P<route>/[a-zA-Z0-9_\-]+)['"]""")

def scan_dart() -> Dict[str, List[str]]:
    api_urls: Set[str] = set()
    raw_paths: Set[str] = set()
    routes: Set[str] = set()
    for root, _dirs, files in os.walk(UI_ROOT):
        for f in files:
            if not f.endswith(".dart"): continue
            p = os.path.join(root, f)
            s = open(p, encoding="utf-8").read()
            for m in HTTP_RE.finditer(s):
                api_urls.add(m.group("url"))
            for m in RAW_PATH_RE.finditer(s):
                raw_paths.add(m.group(1))
            for m in ROUTE_PUSH_RE.finditer(s):
                routes.add(m.group("route"))
    return {"api_urls": sorted(api_urls), "raw_paths": sorted(raw_paths), "push_routes": sorted(routes)}

if __name__ == "__main__":
    print(json.dumps(scan_dart(), indent=2))
