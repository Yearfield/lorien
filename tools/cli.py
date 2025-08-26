from __future__ import annotations
import os, sys, shutil, argparse, sqlite3, time
from pathlib import Path
from core.storage.path import get_db_path

def _ensure_sqlite3() -> bool:
    return shutil.which("sqlite3") is not None

def cmd_show_db_path(args):
    print(str(get_db_path()))

def cmd_backup(args):
    db = get_db_path()
    target = Path(args.target) if args.target else (db.parent / f"lorien_backup_{time.strftime('%Y%m%d_%H%M%S')}.db")
    target = target.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    if not db.exists():
        print(f"[ERROR] DB not found: {db}", file=sys.stderr)
        sys.exit(1)
    if _ensure_sqlite3():
        os.system(f"sqlite3 '{db}' \".backup '{target}'\"")
    else:
        # BEST EFFORT fallback: checkpoint WAL then copy
        with sqlite3.connect(db) as conn:
            conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        shutil.copy2(db, target)
    size = target.stat().st_size if target.exists() else 0
    print(f"[OK] Backup created: {target} ({size} bytes)")

def cmd_restore(args):
    bkp = Path(args.backup).resolve()
    db  = get_db_path()
    if not bkp.exists():
        print(f"[ERROR] Backup not found: {bkp}", file=sys.stderr)
        sys.exit(1)
    # remove stale WAL/SHM
    for suf in ("-wal","-shm"):
        try: (db.parent / (db.name + suf)).unlink()
        except: pass
    if _ensure_sqlite3():
        tmp = Path(str(db) + ".restore.tmp")
        os.system(f"sqlite3 '{tmp}' \".restore '{bkp}'\"")
        # sanity
        with sqlite3.connect(tmp) as conn:
            tbl = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'").fetchone()
            ok  = conn.execute("PRAGMA integrity_check;").fetchone()
            if not tbl or not ok or ok[0] != "ok":
                print("[ERROR] Restore sanity failed", file=sys.stderr)
                sys.exit(1)
        tmp.replace(db)
    else:
        shutil.copy2(bkp, db)
    print(f"[OK] Restored DB to: {db}")

def cmd_wal_checkpoint(args):
    db = get_db_path()
    with sqlite3.connect(db) as conn:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    print("[OK] WAL checkpointed")

def main():
    p = argparse.ArgumentParser(prog="dt", description="Lorien tools")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("show-db-path"); s.set_defaults(func=cmd_show_db_path)
    s = sub.add_parser("backup"); s.add_argument("--target"); s.set_defaults(func=cmd_backup)
    s = sub.add_parser("restore"); s.add_argument("backup"); s.set_defaults(func=cmd_restore)
    s = sub.add_parser("wal-checkpoint"); s.set_defaults(func=cmd_wal_checkpoint)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
