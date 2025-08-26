# Medical Safety Notice

- This software provides **decision support tooling** and optional **LLM-generated suggestions** for text fields.
- It **does not diagnose** or prescribe, and **must not** replace clinician judgment.
- The LLM is guidance-only and refuses dosing/prescriptions. Always follow local protocols.

# Privacy

- The API avoids logging full prompts by default.
- SQLite DB stores decision-tree structure and triage/actions text; do not store PHI unless you have proper safeguards.
