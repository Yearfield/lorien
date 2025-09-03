# Legacy Tests

This directory contains legacy tests that use Mockito and are excluded from the analyzer.

## Why Excluded

These tests use the `mockito` package which is not available in the current dependencies and causes analyzer errors. The tests also use abstract Dio stubs that are no longer compatible with the current Dio version.

## Files

- `repository/` - Repository tests using Mockito mocks
- `golden/` - Golden file tests (if any)

## Future Plans

These tests should be modernized to use:
- `mocktail` instead of `mockito` for mocking
- Proper Dio fakes instead of abstract stubs
- Updated test patterns compatible with current Flutter/Dart versions

## Current Status

Excluded from `flutter analyze` via `analysis_options.yaml` to prevent build failures while preserving the test code for future modernization.
