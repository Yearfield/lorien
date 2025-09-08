#!/usr/bin/env python3
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAT = re.compile(r'\b(BP|High|Low|TestVM|Pulse|Vital Measurement|Node 1|Node1|A|B)\b', re.I)

hits = []
for root, dirs, files in os.walk(ROOT):
    if any(s in root for s in ("/.git", "/venv", "/build", "/.dart_tool")):
        continue
    for f in files:
        if f.endswith((".py", ".sql", ".dart", ".csv", ".xlsx", ".json", ".md", ".yaml", ".yml", ".txt")):
            p = os.path.join(root, f)
            try:
                with open(p, "rb") as fh:
                    b = fh.read(2000000)
                s = b.decode("utf-8", "ignore")
            except Exception:
                continue
            for m in PAT.finditer(s):
                line = s[:m.start()].count("\n") + 1
                hits.append((p, line, m.group(0)))

for p, l, tok in hits[:500]:
    print(f"{p}:{l}: {tok}")

print(f"\nTotal hits: {len(hits)}")
