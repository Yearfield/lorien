from __future__ import annotations
import os, shutil
from pathlib import Path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.storage.path import get_db_path

LEGACY_LOCATIONS = [
    Path("app.db"),
    Path("data/app.db"),
]

def main():
    target = get_db_path()
    moved = False
    for cand in LEGACY_LOCATIONS:
        c = cand.resolve()
        if c.exists() and c != target:
            print(f"Found legacy DB at {c}, moving to {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(c, target)
            moved = True
            break
    if not moved:
        print("No legacy DB found; nothing to migrate.")
    else:
        print("Migration complete.")
    print(f"Current DB path: {target}")

if __name__ == "__main__":
    main()
