# API Header Source of Truth (SoT)

This document defines the canonical 8-column header for Lorien API responses. This header is frozen and must not be changed without explicit approval.

## Canonical 8-Column Header

The following header is the single source of truth for all API responses that include column headers:

```
Vital Measurement, Node 1, Node 2, Node 3, Node 4, Node 5, Diagnostic Triage, Actions
```

## Usage Guidelines

1. **Frozen Header**: This header format is frozen and must not be modified
2. **Consistent Spacing**: Use exactly one space after each comma
3. **Case Sensitivity**: Maintain exact case as shown above
4. **No Additional Columns**: Do not add or remove columns
5. **Order Preservation**: Maintain the exact order of columns

## Where This Header Is Used

- CSV export endpoints (`/api/v1/tree/export`)
- Excel export functionality
- Data import validation
- Documentation examples
- Test fixtures

## Change Control

Any changes to this header require:
1. Explicit approval from the project maintainer
2. Update to this SoT document
3. Update to all affected endpoints
4. Update to all documentation references
5. Update to all test fixtures

## Version History

- **v1.0** (2024-01-01): Initial 8-column header definition
- **v6.0** (2024-12-01): Header frozen for GA release

## References

- [API Routes Registry](./API_ROUTES_REGISTRY.md)
- [Export Documentation](./EXPORT_FORMATS.md)
- [Import Documentation](./IMPORT_FORMATS.md)
