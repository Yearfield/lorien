# Backup & Restore

This project uses **SQLite in WAL mode** for performance. That means there can be sidecar files:
- `app.db` (main database)
- `app.db-wal` (write-ahead log)
- `app.db-shm` (shared memory)

When restoring from a backup, **stale WAL/SHM can resurrect old state**. Our tooling removes them and uses `sqlite3`'s logical copy to keep restores correct.

## Where is my DB?

**Env-first:**
- `DB_PATH` (if set) is used everywhere (API, tools, scripts).

**Defaults:**
- Linux: `~/.local/share/lorien/app.db`
- macOS: `~/Library/Application Support/lorien/app.db`
- Windows: `%APPDATA%\lorien\app.db`

**Run:**
```bash
python -m tools.cli show-db-path
```

## Backing up (recommended)

If sqlite3 is available:

```bash
python -m tools.cli backup
# or bash: DB_PATH=/path/to/app.db tools/scripts/backup_db.sh
```

This uses sqlite3 `.backup` to take a consistent snapshot even if the DB is open.

Expected output includes the target path and a size > 4096 bytes.

## Restoring

```bash
python -m tools.cli restore /path/to/lorien_backup_YYYYMMDD_HHMMSS.db
# or bash: DB_PATH=/path/to/app.db tools/scripts/restore_db.sh /path/to/backup.db
```

**What it does:**

1. Removes any `-wal` / `-shm` sidecar files for the target DB.
2. Uses sqlite3 `.restore` into a temp DB and atomically moves it into place.
3. Verifies schema and `PRAGMA integrity_check = ok`.

After restore, the directory should not contain `app.db-wal` or `app.db-shm` until the app opens the DB again.

## Troubleshooting

**Backup is ~4096 bytes**
A DB header without pages; ensure the app committed/closed or use the provided backup command (it snapshots safely).

**Restore succeeded but data missing**
Likely stale WAL was reapplied. Use our restore command which removes WAL/SHM and performs a logical restore.

**Permission denied**
Ensure you have write access to the DB location. On Windows, stop any process holding the DB.

**Find the DB path used by the API**
```bash
curl http://localhost:8000/health → see db.path.
```

## Automation

**Makefile targets (optional):**

```bash
make backup → calls the script with DB_PATH
make restore BACKUP=/path/to/backup.db → runs restore script
```
