# Lorien UI — Release Checklist (Phase-6D+)

## Pre-Release Validation
- [ ] `flutter clean && flutter pub get`
- [ ] `dart format . && flutter analyze` (0 issues)
- [ ] `flutter test --coverage` (>=20% coverage)
- [ ] All goldens up-to-date (if any): `flutter test --update-goldens` (manual)
- [ ] UI_STATE_REPORT.md updated (analyze count, test totals, endpoints)
- [ ] Version bump in pubspec.yaml
- [ ] CHANGELOG.md updated (added: TreeApi fallback, 422 duplicate mapping)
- [ ] Build artifacts: Linux, Android (emulator sanity), iOS (simulator sanity)
- [ ] Tag & push (e.g., v0.7.0)
- [ ] Post-merge smoke: run integration_test

## Release Notes Template
```markdown
## 0.7.0
- Unify children endpoint to `/tree/{id}/children` with 404->legacy fallback.
- Add duplicate_child_label per-slot 422 mapping.
- Stabilize tests & mocks; 0 analyze issues; 50+ tests green.
- CI coverage gate (>=20%); add integration smoke.
```

## Manual Verification Checklist
- [ ] Edit Tree: type quickly; caret never jumps; Ctrl+S saves once.
- [ ] 422 duplicate: mock PUT → inline error shows on the correct slot only.
- [ ] 409 conflict: banner with Reload; reload hydrates and preserves user text.
- [ ] Dictionary suggestions: ≥2 chars → overlay; tap inserts.
- [ ] Next Incomplete: CTA navigates; unsaved guard prompts when dirty.
- [ ] Batch ops: multiselect + Fill "Other" works on a small set (spot-check).
- [ ] CI shows coverage ≥20%, analyze 0 issues.

## Post-Release
- [ ] Monitor CI for any regressions
- [ ] Update documentation if needed
- [ ] Notify team of release completion
