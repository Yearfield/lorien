#!/usr/bin/env bash
set -euo pipefail

# Nightly Audit Retention Rotation Script
# This script should be run via cron job (e.g., daily at 2 AM)

# Configuration
DB_PATH="${DB_PATH:-sqlite.db}"
LOG_FILE="${LOG_FILE:-/var/log/lorien/audit_rotation.log}"
BACKUP_DIR="${BACKUP_DIR:-backups}"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting audit retention rotation for $DB_PATH"

# Check if database exists
if [[ ! -f "$DB_PATH" ]]; then
    log "ERROR: Database file $DB_PATH not found"
    exit 1
fi

# Create backup before rotation
if [[ -d "$BACKUP_DIR" ]]; then
    BACKUP_FILE="$BACKUP_DIR/audit_pre_rotation_$(date +%Y%m%d_%H%M%S).db"
    cp "$DB_PATH" "$BACKUP_FILE"
    log "Created backup: $BACKUP_FILE"
fi

# Run retention script
if sqlite3 "$DB_PATH" < scripts/audit_retention_sqlite.sql; then
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
if [[ -d "$BACKUP_DIR" ]]; then
    find "$BACKUP_DIR" -name "audit_pre_rotation_*.db" -mtime +7 -delete
    log "Cleaned up old rotation backups"
fi

log "Audit retention rotation complete"
