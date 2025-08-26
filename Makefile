# Lorien Makefile
# Convenience targets for common operations

DB_PATH ?= $(HOME)/.local/share/lorien/app.db

.PHONY: help backup restore show-db-path test clean

help:
	@echo "Available targets:"
	@echo "  backup          - Create database backup"
	@echo "  restore BACKUP  - Restore database from backup file"
	@echo "  show-db-path    - Show current database path"
	@echo "  test            - Run all tests"
	@echo "  clean           - Clean up temporary files"

backup:
	@echo "Creating backup..."
	DB_PATH="$(DB_PATH)" bash tools/scripts/backup_db.sh

restore:
	@if [ -z "$(BACKUP)" ]; then \
		echo "Usage: make restore BACKUP=path/to/backup.db"; \
		exit 1; \
	fi
	@echo "Restoring from $(BACKUP)..."
	DB_PATH="$(DB_PATH)" bash tools/scripts/restore_db.sh "$(BACKUP)"

show-db-path:
	@python -m tools.cli show-db-path

test:
	@echo "Running tests..."
	python -m pytest tests/ -v

clean:
	@echo "Cleaning up..."
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.tmp" -delete
	find . -name "*.restore.*" -delete
