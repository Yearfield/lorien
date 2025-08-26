# Optional Local LLM

**Off by default.** Enable only if you have a local GGUF model (e.g., your II-medical build) and want suggestions for *Diagnostic Triage* and *Actions*.

## Enable

```bash
export LLM_ENABLED=true
export LLM_MODEL_PATH=/path/to/II-medical.gguf
# Optional tuning:
export LLM_N_THREADS=8
export LLM_N_CTX=2048
export LLM_N_GPU_LAYERS=0   # 0 = CPU-only
export LLM_MAX_TOKENS=160
```

## Endpoint

```http
POST /llm/fill-triage-actions
{
  "root": "Fever",
  "nodes": ["Infant", "Irritable", "Poor feeding"],
  "triage_style": "diagnosis-only",
  "actions_style": "referral-only",
  "apply": false,
  "node_id": 123   // only when apply=true; must be a leaf
}
```

**Returns:**
```json
{ "diagnostic_triage": "...", "actions": "...", "applied": false }
```

## Safety

Guidance-only. No dosing/prescriptions or diagnoses. Dangerous requests are refused.

The app clamps output length and requests JSON only.

**Disable anytime:** `export LLM_ENABLED=false`.

## Notes

This code is model-agnostic; point it at your chosen GGUF (e.g., II-medical).

For structured, succinct outputs, we request JSON with two keys only.
