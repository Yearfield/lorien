# Lorien Documentation

Welcome to the Lorien documentation. This directory contains comprehensive documentation for the Lorien decision-tree application.

## Documentation Structure

- **[Architecture.md](./Architecture.md)** - System overview and key decisions
- **[API_HEADER_SOT.md](./API_HEADER_SOT.md)** - Single source of truth for the 8-column header
- **[API_ROUTES_REGISTRY.md](./API_ROUTES_REGISTRY.md)** - Canonical API endpoints
- **[API.md](./API.md)** - Narrative API guide and contracts
- **[IMPORT_FORMATS.md](./IMPORT_FORMATS.md)** / **[EXPORT_FORMATS.md](./EXPORT_FORMATS.md)** - Data contracts
- **[DEVELOPMENT.md](./DEVELOPMENT.md)** / **[Dev_Quickstart.md](./Dev_Quickstart.md)** - Setup and configuration
- **[Monitoring_Telemetry.md](./Monitoring_Telemetry.md)** - Health, metrics, SLOs
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Deployment & operations
- **[Backup_Restore.md](./Backup_Restore.md)** - Backup/restore
- **[UI_Guide.md](./UI_Guide.md)** - User interface guide including Dictionary pane
- **[EngineShelob_Guide.md](./EngineShelob_Guide.md)** - Pathogen data import and management system

## Quick Start

1. See [DEVELOPMENT.md](./DEVELOPMENT.md) for setup instructions
2. See [API_ROUTES_REGISTRY.md](./API_ROUTES_REGISTRY.md) for API reference
3. See [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment options
4. See [RELEASE_PROCESS.md](./RELEASE_PROCESS.md) for releasing

## Contributing

When updating documentation:

1. Follow the established patterns
2. Update the relevant SoT documents
3. Run the documentation audit: `python tools/audit/docs_audit.py`
4. Ensure all tests pass: `pytest tests/contracts/`
5. Follow the release flow: `docs/RELEASE_PROCESS.md`

## Archive

Stale or outdated documentation is archived in the `_archive/` directory with tombstone headers explaining why it was archived.
