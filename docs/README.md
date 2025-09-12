# Lorien Documentation

Welcome to the Lorien documentation. This directory contains comprehensive documentation for the Lorien decision-tree application.

## Documentation Structure

- **[API_HEADER_SOT.md](./API_HEADER_SOT.md)** - Single source of truth for the 8-column API header
- **[API_ROUTES_REGISTRY.md](./API_ROUTES_REGISTRY.md)** - Canonical API endpoints registry
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** - Development setup and guidelines
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Deployment instructions and configuration

## Quick Start

1. See [DEVELOPMENT.md](./DEVELOPMENT.md) for setup instructions
2. See [API_ROUTES_REGISTRY.md](./API_ROUTES_REGISTRY.md) for API reference
3. See [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment options

## Contributing

When updating documentation:
1. Follow the established patterns
2. Update the relevant SoT documents
3. Run the documentation audit: `python tools/audit/docs_audit.py`
4. Ensure all tests pass: `pytest tests/contracts/`

## Archive

Stale or outdated documentation is archived in the `_archive/` directory with tombstone headers explaining why it was archived.
