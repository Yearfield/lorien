#!/usr/bin/env bash
set -euo pipefail

echo -e "\033[0;32m[INFO]\033[0m Starting Lorien database backup..."
APP_NAME="${APP_NAME:-lorien}"

# Resolve DB_PATH (env wins)
if [[ -n "${DB_PATH:-}" ]]; then
  DB="${DB_PATH}"
  echo -e "\033[0;32m[INFO]\033[0m Using DB_PATH from env: $DB"
else
  # Python one-liner to mimic get_db_path() logic if needed
  DB="${HOME}/.local/share/${APP_NAME}/app.db"
  echo -e "\033[0;32m[INFO]\033[0m Using default DB path: $DB"
fi

if [[ ! -f "$DB" ]]; then
  echo -e "\033[0;31m[ERROR]\033[0m Database file not found at: $DB"
  exit 1
fi

ts="$(date +%Y%m%d_%H%M%S)"
TARGET_DIR="$(dirname "$DB")"
TARGET="${TARGET_DIR}/lorien_backup_${ts}.db"

echo -e "\033[0;32m[INFO]\033[0m Source: $DB"
echo -e "\033[0;32m[INFO]\033[0m Target: $TARGET"

src_size=$(stat -c%s "$DB" 2>/dev/null || echo 0)
echo -e "\033[0;32m[INFO]\033[0m Source file size: ${src_size} bytes"

# Prefer consistent snapshot using sqlite3 .backup; fallback to cp if sqlite3 missing
if command -v sqlite3 >/dev/null 2>&1; then
  sqlite3 "$DB" ".backup '${TARGET}'"
else
  cp -f "$DB" "$TARGET"
fi

tgt_size=$(stat -c%s "$TARGET" 2>/dev/null || echo 0)
echo -e "\033[0;32m[INFO]\033[0m Backup size: ${tgt_size} bytes"

if [[ "$tgt_size" -le 4096 ]]; then
  echo -e "\033[0;33m[WARN]\033[0m Backup looks empty (<= 4096 bytes). Did you flush/close the DB before backup?"
fi

echo -e "\033[0;32m[SUCCESS]\033[0m Backup created: $TARGET"
