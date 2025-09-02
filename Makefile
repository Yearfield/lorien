# Lorien Development Makefile

.PHONY: help dev test clean install migrate prune-flags

# Default target
help:
	@echo "Lorien Development Commands:"
	@echo ""
	@echo "  dev      - Start development server with virtual environment"
	@echo "  test     - Run tests"
	@echo "  clean    - Clean up temporary files and build artifacts"
	@echo "  install  - Install dependencies"
	@echo "  migrate  - Run database migrations"
	@echo "  prune-flags - Prune flag audit table (30d/50k retention)"
	@echo "  lint     - Run code linting"
	@echo "  format   - Format code with black"
	@echo ""

# Development server
dev:
	@echo "Setting up development environment..."
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
	@echo "Starting development server..."
	LORIEN_DB_PATH=$$(pwd)/.tmp/lorien.db uvicorn api.app:app --host 127.0.0.1 --port 8000 --reload

# Run tests
test:
	@echo "Running tests..."
	pytest -q

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf .venv
	rm -rf .tmp
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf .pytest_cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	@echo "Cleanup complete"

# Install dependencies
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

# Run database migrations
migrate:
	@echo "Running database migrations..."
	python storage/migrate.py

# Prune flag audit table
prune-flags:
	@echo "Pruning flag audit table..."
	python ops/prune_flags.py

# Lint code
lint:
	@echo "Running code linting..."
	flake8 api/ core/ storage/ tests/
	pylint api/ core/ storage/ tests/

# Format code
format:
	@echo "Formatting code..."
	black api/ core/ storage/ tests/

# Quick health check
health:
	@echo "Checking API health..."
	curl -s http://127.0.0.1:8000/api/v1/health | jq .

# Check LLM status
llm-status:
	@echo "Checking LLM status..."
	curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/api/v1/llm/health

# Start with LLM enabled
dev-llm:
	@echo "Starting development server with LLM enabled..."
	LLM_ENABLED=true LORIEN_DB_PATH=$$(pwd)/.tmp/lorien.db uvicorn api.app:app --host 127.0.0.1 --port 8000 --reload

# Start with CORS allowed for LAN
dev-lan:
	@echo "Starting development server with CORS allowed for LAN..."
	CORS_ALLOW_ALL=true LORIEN_DB_PATH=$$(pwd)/.tmp/lorien.db uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload

# Flutter development
flutter-dev:
	@echo "Starting Flutter development..."
	cd ui_flutter && flutter run -d linux --dart-define=API_BASE_URL=http://127.0.0.1:8000/api/v1

# Flutter test
flutter-test:
	@echo "Running Flutter tests..."
	cd ui_flutter && flutter test

# Flutter build
flutter-build:
	@echo "Building Flutter app..."
	cd ui_flutter && flutter build linux

# Streamlit development
streamlit-dev:
	@echo "Starting Streamlit development..."
	cd ui_streamlit && streamlit run app.py --server.port 8501

# Full development setup
setup: install migrate
	@echo "Development environment setup complete!"
	@echo "Run 'make dev' to start the development server"
	@echo "Run 'make flutter-dev' to start Flutter development"
	@echo "Run 'make streamlit-dev' to start Streamlit development"
