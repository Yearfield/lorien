import json, re
from pathlib import Path

CODE_BLOCK = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL)

def test_json_snippets_are_valid():
    root = Path(__file__).resolve().parents[2] / "docs"
    bad = []
    for p in root.rglob("*.md"):
        text = p.read_text(encoding="utf-8")
        for m in CODE_BLOCK.finditer(text):
            blob = m.group(1)
            # Skip placeholder content that's not meant to be valid JSON
            if "..." in blob or "//" in blob or "..." in blob:
                continue
            try:
                json.loads(blob)
            except Exception as e:
                bad.append((str(p), str(e), blob[:120]))
    assert not bad, "Invalid JSON in docs:\n" + "\n".join(f"{f}: {err}" for f, err, _ in bad)
