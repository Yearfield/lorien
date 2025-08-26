#!/usr/bin/env bash
set -euo pipefail

RED=$'\033[0;31m'; GRN=$'\033[0;32m'; YEL=$'\033[0;33m'; NC=$'\033[0m'

if [[ $# -lt 1 ]]; then
  echo -e "${RED}[ERROR]${NC} Usage: $0 <backup_file.db>"
  exit 1
fi

BACKUP="$1"
APP_NAME="${APP_NAME:-lorien}"

# Resolve destination DB (env wins)
if [[ -n "${DB_PATH:-}" ]]; then
  DB="${DB_PATH}"
  echo -e "${GRN}[INFO]${NC} Using DB_PATH from env: $DB"
else
  DB="${HOME}/.local/share/${APP_NAME}/app.db"
  echo -e "${GRN}[INFO]${NC} Using default DB path: $DB"
fi

if [[ ! -f "$BACKUP" ]]; then
  echo -e "${RED}[ERROR]${NC} Backup file not found: $BACKUP"
  exit 1
fi

bkp_size=$(stat -c%s "$BACKUP" 2>/dev/null || echo 0)
echo -e "${GRN}[INFO]${NC} Backup size: ${bkp_size} bytes"

if [[ "$bkp_size" -le 4096 ]]; then
  echo -e "${RED}[ERROR]${NC} File must be a valid Lorien SQLite database (too small)."
  exit 1
fi

mkdir -p "$(dirname "$DB")"

# Print dir contents for diagnostics
echo -e "${GRN}[INFO]${NC} Target dir before restore:"
ls -la "$(dirname "$DB")" || true

# If sqlite3 available, use logical restore into a temp DB; otherwise, cp fallback.
if command -v sqlite3 >/dev/null 2>&1; then
  # Remove stale WAL/SHM to avoid reapplying old journal on next open
  rm -f "${DB}-wal" "${DB}-shm" || true

  TMPDB="$(mktemp "${DB}.restore.XXXXXX")"
  # Use .restore to load the backup into a fresh DB file
  sqlite3 "$TMPDB" ".restore '${BACKUP}'"

  # Basic sanity on temp DB
  if ! sqlite3 "$TMPDB" "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes';" | grep -q "^nodes$"; then
    echo -e "${RED}[ERROR]${NC} Restored temp DB missing 'nodes' table."
    rm -f "$TMPDB"
    exit 1
  fi
  if ! sqlite3 "$TMPDB" "PRAGMA integrity_check;" | grep -q "^ok$"; then
    echo -e "${RED}[ERROR]${NC} Restored temp DB failed integrity check."
    rm -f "$TMPDB"
    exit 1
  fi

  # Atomically move into place
  mv -f "$TMPDB" "$DB"
else
  # Fallback: hard replace main DB file; also remove stale WAL/SHM
  rm -f "$DB" "${DB}-wal" "${DB}-shm" || true
  cp -f "$BACKUP" "$DB"
fi

# Post-restore diagnostics
echo -e "${GRN}[INFO]${NC} Target dir after restore:"
ls -la "$(dirname "$DB")" || true

dst_size=$(stat -c%s "$DB" 2>/dev/null || echo 0)
echo -e "${GRN}[INFO]${NC} Restored DB size: ${dst_size} bytes"

# Final sanity: verify nodes table exists and integrity is ok
if command -v sqlite3 >/dev/null 2>&1; then
  if ! sqlite3 "$DB" "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes';" | grep -q "^nodes$"; then
    echo -e "${RED}[ERROR]${NC} Restored DB missing 'nodes' table."
    exit 1
  fi
  if ! sqlite3 "$DB" "PRAGMA integrity_check;" | grep -q "^ok$"; then
    echo -e "${RED}[ERROR]${NC} Restored DB failed integrity check."
    exit 1
  fi
  
  # Optional: ensure consistent WAL state from the start
  sqlite3 "$DB" "PRAGMA journal_mode=WAL; PRAGMA wal_checkpoint(TRUNCATE);"
fi

echo -e "${GRN}[SUCCESS]${NC} Database restored to: $DB"
