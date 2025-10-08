#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RETENTION_SQL="${REPO_ROOT}/scripts/audit_retention_sqlite.sql"

# Resolve default DB path via core.storage.path.get_db_path when DB_PATH not provided
if [[ -z "${DB_PATH:-}" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    DB_PATH="$(PYTHONPATH="${REPO_ROOT}:${PYTHONPATH:-}" python3 <<'PY' 2>/dev/null || echo "")
from core.storage.path import get_db_path
print(get_db_path())
PY
)"
  fi
  if [[ -z "$DB_PATH" ]]; then
    DB_PATH="$HOME/.local/share/lorien/app.db"
  fi
fi

# Nightly Audit Retention Rotation Script
# This script should be run via cron job (e.g., daily at 2 AM)

# Configuration
LOG_FILE="${LOG_FILE:-/var/log/lorien/audit_rotation.log}"
BACKUP_DIR="${BACKUP_DIR:-${REPO_ROOT}/backups/audit_rotation}"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"
# Ensure backup directory exists if configured
mkdir -p "$BACKUP_DIR"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting audit retention rotation for $DB_PATH"

# Ensure sqlite3 is available
if ! command -v sqlite3 >/dev/null 2>&1; then
    log "ERROR: sqlite3 command not found"
    exit 1
fi

# Check if database exists
if [[ ! -f "$DB_PATH" ]]; then
    log "ERROR: Database file $DB_PATH not found"
    exit 1
fi

# Create backup before rotation
BACKUP_FILE="$BACKUP_DIR/audit_pre_rotation_$(date +%Y%m%d_%H%M%S).db"
sqlite3 "$DB_PATH" ".backup '${BACKUP_FILE}'"
log "Created backup: $BACKUP_FILE"

# Run retention script
if sqlite3 "$DB_PATH" < "$RETENTION_SQL"; then
    log "Audit retention rotation completed successfully"

    # Get retention status
    STATUS=$(sqlite3 "$DB_PATH" "SELECT retention_status FROM audit_retention_status LIMIT 1" 2>/dev/null || echo "UNKNOWN")
    TOTAL_ROWS=$(sqlite3 "$DB_PATH" "SELECT total_rows FROM audit_retention_status LIMIT 1" 2>/dev/null || echo "UNKNOWN")

    log "Retention status: $STATUS, Total rows: $TOTAL_ROWS"
else
    log "ERROR: Audit retention rotation failed"
    exit 1
fi

# Cleanup old backups (keep last 7 days)
find "$BACKUP_DIR" -name "audit_pre_rotation_*.db" -mtime +7 -delete
log "Cleaned up old rotation backups"

log "Audit retention rotation complete"
