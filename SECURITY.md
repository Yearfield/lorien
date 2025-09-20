# Security Policy

## Supported Versions
- Active development branch (main) — security fixes accepted
- Tagged prereleases — fixes on a best‑effort basis

## Reporting a Vulnerability
- Email: security@lorien.local (placeholder)
- Please include: affected component, reproduction steps, impact, and any logs.
- We aim to acknowledge within 72 hours and provide a remediation plan within 7 days.

## Scope & Data Handling
- No PHI should be stored or transmitted. Lorien stores decision‑tree structure and free‑text triage/actions only.
- Logs redact sensitive headers. Avoid dumping full prompts or payloads in logs.

## Dependencies & Updates
- Python dependencies pinned via `requirements.txt`; Flutter via `pubspec.yaml`.
- Weekly dependency review and security updates during beta.

## LLM Guidance Guardrails
- LLM features are OFF by default.
- When enabled, outputs are guidance‑only; no dosing/prescriptions.
- Requests must adhere to JSON‑only contracts; inputs/outputs are clamped and validated.

