import argparse
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]

KEEP_DIRS = [
    "api",
    "Engines/EngineLongBow",
    "ui_flutter/lib/features/vm_builder",
    "ui_flutter/lib/main.dart",
    "api/db/migrations",
]

SKIP_DIRS = {"__pycache__", ".venv", "venv", "site-packages", "build", "dist"}
SKIP_SUFFIXES = {".pyc"}


def list_tree(base):
    base_path = ROOT / base
    items = []
    if base_path.is_file():
        return [str(base_path.relative_to(ROOT))]
    for p in base_path.rglob("*"):
        # skip directories by name anywhere in path
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.is_file() and p.suffix not in SKIP_SUFFIXES:
            items.append(str(p.relative_to(ROOT)))
    return sorted(items)


def build_summary():
    summary = {}
    for d in KEEP_DIRS:
        summary[d] = list_tree(d)
    # API routes quick peek
    routes = []
    app_py = (ROOT / "api" / "app.py").read_text(encoding="utf-8", errors="ignore")
    for line in app_py.splitlines():
        if "include_router" in line:
            routes.append(line.strip())
    summary["api.routes"] = routes
    return summary


def pretty(summary: dict):
    print("PROJECT INVENTORY")
    print("──────────────────")
    # Routers
    routes = summary.get("api.routes", [])
    print("\nAPI Routers mounted:")
    for r in routes:
        print(f"  - {r}")
    # Buckets
    buckets = [
        ("Backend (api)", "api"),
        ("Engine (LongBow)", "Engines/EngineLongBow"),
        ("Migrations", "api/db/migrations"),
        ("Flutter VM Builder", "ui_flutter/lib/features/vm_builder"),
        ("Flutter App Entrypoint", "ui_flutter/lib/main.dart"),
    ]
    for title, key in buckets:
        items = summary.get(key, [])
        print(f"\n{title}:")
        if isinstance(items, list):
            for p in items:
                print(f"  - {p}")
        else:
            print(f"  - {items}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()
    summary = build_summary()
    if args.pretty:
        pretty(summary)
    else:
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
